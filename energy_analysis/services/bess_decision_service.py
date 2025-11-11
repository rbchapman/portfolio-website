from typing import Dict, List
from ..models import BESSConfig
from .daily_summary_service import DailySummaryService
import logging

logger = logging.getLogger(__name__)


class BESSDecisionService:
    """
    Simple BESS operational decision analysis.
    Pure Python - no pandas, no magic, fully explainable.
    """
    
    @staticmethod
    def analyze_day(date_string: str, config: BESSConfig) -> Dict:
        """
        Main entry point: analyze a full day of BESS operations.
        
        Args:
            date_string: Date in 'YYYY-MM-DD' format
            config: BESSConfig with battery specifications
            
        Returns:
            Dict with hourly decisions and daily performance summary
        """
        # Get the day's data (uses your existing service!)
        summary, _ = DailySummaryService.get_or_create_summary(date_string)
        hourly_data = summary.hourly_data_json['hourly_data']

        if not hourly_data:
            logger.warning(f"No hourly data found for {date_string}")
            return {'error': f'No data for {date_string}'}
        
        prices = []
        for hour in hourly_data:
            price = hour.get('price') or hour.get('value') or hour.get('marginalpdbc')
            if price is not None:
                prices.append(price)
            else:
                logger.warning(f"⚠️ Missing price for {date_string} hour {hour.get('hour')}: keys={list(hour.keys())}")
        # Calculate price percentiles for decision-making
        prices = [hour['price'] for hour in hourly_data]
        
        # Track battery state throughout the day
        current_soc = 10.0  # Assuming day starts with an empty battery
        
        # Process each hour
        decisions = []
        for hour_data in hourly_data:
            decision = BESSDecisionService._make_decision(
                hour_data=hour_data,
                all_day_prices=prices,
                current_soc=current_soc,
                config=config
            )
            decisions.append(decision)
            current_soc = decision['soc_after']
        
        # Calculate daily performance
        performance = BESSDecisionService._calculate_performance(decisions, config)
        
        return {
            'date': date_string,
            'config': config.to_dict(),
            'hourly_decisions': decisions,
            'daily_performance': performance,
            'data_source': summary.data_source
        }
    

    @staticmethod
    def _make_decision(
        hour_data: Dict, 
        all_day_prices: List[float],
        current_soc: float,
        config: BESSConfig
    ) -> Dict:
        """
        Smart decision logic: Use percentiles BUT only if there's a meaningful price spread
        """
        price = hour_data['price']
        
        # Calculate daily price statistics
        min_price = min(all_day_prices)
        max_price = max(all_day_prices)
        price_spread = max_price - min_price
        
        # Only do arbitrage if there's meaningful spread (at least €15/MWh)
        if price_spread < 15:
            # Flat price day - don't trade
            action = 'HOLD'
            energy_mwh = 0
            cost = 0
            new_soc = current_soc
        else:
            # Good spread - use percentile logic
            sorted_prices = sorted(all_day_prices)
            price_rank = sorted_prices.index(price) if price in sorted_prices else 0
            price_percentile = (price_rank / len(sorted_prices)) * 100
            
            CHARGE_THRESHOLD = 30  # Bottom 30% of prices
            DISCHARGE_THRESHOLD = 70  # Top 30% of prices
            
            if price_percentile < CHARGE_THRESHOLD and current_soc < config.max_soc:
                action = 'CHARGE'
                energy_mwh, cost, new_soc = BESSDecisionService._calculate_charge(
                    current_soc, config, price
                )
            elif price_percentile > DISCHARGE_THRESHOLD and current_soc > config.min_soc:
                action = 'DISCHARGE'
                energy_mwh, cost, new_soc = BESSDecisionService._calculate_discharge(
                    current_soc, config, price
                )
            else:
                action = 'HOLD'
                energy_mwh = 0
                cost = 0
                new_soc = current_soc
        
        # Build reasoning
        reasoning = BESSDecisionService._build_reasoning(
            action, price, price_spread, hour_data, current_soc, config
        )
        
        return {
            'hour': hour_data['hour'],
            'action': action,
            'price': round(price, 2),
            'price_spread': round(price_spread, 2),
            'net_load': round(hour_data.get('net_load', hour_data['demand'] - hour_data['vre_total']), 1),
            'vre_pct': round(hour_data['vre_pct'], 1),
            'energy_mwh': round(energy_mwh, 1),
            'cost_eur': round(cost, 2),
            'soc_before': round(current_soc, 1),
            'soc_after': round(new_soc, 1),
            'reasoning': reasoning
        }
    
    @staticmethod
    def _calculate_charge(current_soc: float, config: BESSConfig, price: float) -> tuple:
        """
        Calculate charging: how much energy, cost, and new SoC.
        
        Simple math you can explain:
        - We can charge at power_mw rate for 1 hour
        - But can't exceed max_soc limit
        - Cost = energy × price
        """
        # Maximum energy we could add in 1 hour
        max_energy = config.power_mw
        
        # But we're limited by how much room is left in battery
        soc_room = config.max_soc - current_soc  # % points available
        capacity_room = (soc_room / 100) * config.capacity_mwh  # MWh available
        
        # Take the smaller of the two
        energy_mwh = min(max_energy, capacity_room)
        
        # Calculate cost (we're spending money to charge)
        cost = energy_mwh * price
        
        # Calculate new SoC
        soc_increase = (energy_mwh / config.capacity_mwh) * 100
        new_soc = min(current_soc + soc_increase, config.max_soc)
        
        return energy_mwh, cost, new_soc
    
    @staticmethod
    def _calculate_discharge(current_soc: float, config: BESSConfig, price: float) -> tuple:
        """
        Calculate discharging: how much energy, revenue, and new SoC.
        
        Key concept - efficiency loss:
        - Battery stored 100 MWh
        - But only 87 MWh comes back out (87% efficient)
        - This is the "round-trip efficiency"
        """
        # Maximum energy we could discharge in 1 hour (accounting for efficiency)
        max_energy = config.power_mw * config.efficiency
        
        # But we're limited by how much energy is available above min_soc
        soc_available = current_soc - config.min_soc  # % points available
        capacity_available = (soc_available / 100) * config.capacity_mwh  # MWh available
        
        # Take the smaller of the two
        energy_mwh = min(max_energy, capacity_available)
        
        # Calculate revenue (negative cost = we earn money)
        cost = -energy_mwh * price  # Negative because we're earning
        
        # Calculate new SoC (discharge removes energy from battery)
        # Note: We remove more energy from battery than we sell (due to efficiency)
        actual_battery_drain = energy_mwh / config.efficiency
        soc_decrease = (actual_battery_drain / config.capacity_mwh) * 100
        new_soc = max(current_soc - soc_decrease, config.min_soc)
        
        return energy_mwh, cost, new_soc
    
    @staticmethod
    def _build_reasoning(
        action: str,
        price: float,
        price_spread: float,
        hour_data: Dict,
        soc: float,
        config: BESSConfig
    ) -> List[str]:
        reasons = []
        
        if price_spread < 15:
            return [f"⚪ Flat price day (€{price_spread:.0f} spread) - arbitrage not profitable"]
        
        if action == 'CHARGE':
            reasons.append(f"✓ Low price hour (€{price:.2f}/MWh)")
            if hour_data['vre_pct'] > 60:
                reasons.append(f"✓ High VRE: {hour_data['vre_pct']:.0f}% renewable")
            
        elif action == 'DISCHARGE':
            reasons.append(f"✓ High price hour (€{price:.2f}/MWh)")
            if hour_data['vre_pct'] < 40:
                reasons.append(f"✓ Peak demand period")
        
        else:
            reasons.append(f"⚪ Mid-range price (€{price:.2f}/MWh)")
        
        return reasons
    
    @staticmethod
    def _calculate_performance(decisions: List[Dict], config: BESSConfig) -> Dict:
        """
        Calculate daily performance metrics.
        
        Simple sums and averages - completely explainable.
        """
        # Separate charge and discharge hours
        charges = [d for d in decisions if d['action'] == 'CHARGE']
        discharges = [d for d in decisions if d['action'] == 'DISCHARGE']
        
        # Financial metrics
        total_charge_cost = sum(d['cost_eur'] for d in charges)
        total_discharge_revenue = sum(-d['cost_eur'] for d in discharges)  # Negative cost = revenue
        gross_profit = total_discharge_revenue - total_charge_cost
        
        # Energy metrics
        total_charged = sum(d['energy_mwh'] for d in charges)
        total_discharged = sum(d['energy_mwh'] for d in discharges)
        
        # Calculate cycles (how many times we "used" the full battery)
        cycles = total_discharged / config.capacity_mwh if config.capacity_mwh > 0 else 0
        
        # Average prices
        avg_charge_price = total_charge_cost / total_charged if total_charged > 0 else 0
        avg_discharge_price = total_discharge_revenue / total_discharged if total_discharged > 0 else 0
        
        return {
            'gross_profit_eur': round(gross_profit, 2),
            'revenue_eur': round(total_discharge_revenue, 2),
            'cost_eur': round(total_charge_cost, 2),
            'energy_charged_mwh': round(total_charged, 1),
            'energy_discharged_mwh': round(total_discharged, 1),
            'avg_charge_price': round(avg_charge_price, 2),
            'avg_discharge_price': round(avg_discharge_price, 2),
            'cycles_completed': round(cycles, 2),
            'charge_hours': len(charges),
            'discharge_hours': len(discharges),
            'utilization_pct': round((total_discharged / config.capacity_mwh) * 100, 1) if config.capacity_mwh > 0 else 0
        }