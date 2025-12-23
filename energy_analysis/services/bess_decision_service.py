"""
BESS Decision Service - Optimal Scheduling with Perfect Foresight

This is a BACKTEST tool. We know all 24 hours of prices in advance,
so we can calculate the mathematically optimal charge/discharge schedule.

The algorithm is simple:
1. Sort hours by price
2. Charge during the cheapest hours
3. Discharge during the most expensive hours
4. Only trade if profitable after efficiency losses

No machine learning, no complex optimization - just sorting and arithmetic.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class BESSDecisionService:
    """
    Optimal BESS scheduling with perfect foresight.
    
    This is a BACKTEST - we use complete knowledge of the day's prices
    to calculate what the optimal trading strategy WOULD HAVE BEEN.
    
    Real-world trading achieves ~60-70% of this theoretical maximum
    due to forecast errors and market constraints.
    """
    
    @staticmethod
    def analyze_day(date_string: str, config) -> Dict:
        """
        Main entry point: find optimal BESS operations for a given day.
        
        Args:
            date_string: Date in 'YYYY-MM-DD' format
            config: BESSConfig with battery specifications
            
        Returns:
            Dict with hourly decisions and daily performance
        """
        # Step 1: Get the day's data using your existing service
        from .daily_summary_service import DailySummaryService
        summary, _ = DailySummaryService.get_or_create_summary(date_string)
        hourly_data = summary.hourly_data_json.get('hourly_data', [])
        
        if not hourly_data:
            return {'error': f'No data for {date_string}'}
        
        # Step 2: Extract hours with valid prices
        hours_with_prices = BESSDecisionService._extract_valid_hours(hourly_data)
        
        if len(hours_with_prices) < 2:
            return {'error': 'Insufficient price data for arbitrage'}
        
        # Step 3: Find optimal schedule
        schedule = BESSDecisionService._find_optimal_schedule(hours_with_prices, config)
        
        if schedule is None:
            # Not profitable - return all HOLD decisions
            decisions = BESSDecisionService._build_hold_decisions(hourly_data, config)
            return {
                'date': date_string,
                'config': config.to_dict(),
                'hourly_decisions': decisions,
                'daily_performance': BESSDecisionService._empty_performance(),
                'data_source': summary.data_source,
                'optimization_note': 'No profitable arbitrage opportunity found'
            }
        
        # Step 4: Build hourly decisions from optimal schedule
        decisions = BESSDecisionService._build_decisions(
            hourly_data, schedule, config
        )
        
        # Step 5: Calculate performance metrics
        performance = BESSDecisionService._calculate_performance(decisions, config)
        
        return {
            'date': date_string,
            'config': config.to_dict(),
            'hourly_decisions': decisions,
            'daily_performance': performance,
            'data_source': summary.data_source,
            'optimization_note': f"Optimal single-cycle: charge {len(schedule['charge_hours'])}h, discharge {len(schedule['discharge_hours'])}h"
        }
    
    # =========================================================================
    # STEP 2: Extract valid hours
    # =========================================================================
    
    @staticmethod
    def _extract_valid_hours(hourly_data: List[Dict]) -> List[Dict]:
        """
        Pull out hours that have valid price data.
        
        We need prices to do arbitrage - no price, no trade.
        
        Returns list of dicts with: index, hour, price, and original data
        """
        valid_hours = []
        
        for i, hour in enumerate(hourly_data):
            price = hour.get('price')
            
            # Skip hours without price data
            if price is None:
                logger.debug(f"Hour {hour.get('hour')} missing price, skipping")
                continue
            
            valid_hours.append({
                'index': i,                    # Position in original list
                'hour': hour.get('hour'),      # "00:00", "01:00", etc.
                'price': float(price),         # €/MWh
                'vre_pct': hour.get('vre_pct', 0),  # For context in output
                'original': hour               # Keep full data for reference
            })
        
        return valid_hours
    
    # =========================================================================
    # STEP 3: Find optimal schedule (THE CORE ALGORITHM)
    # =========================================================================
    
    @staticmethod
    def _find_optimal_schedule(hours_with_prices: List[Dict], config) -> Optional[Dict]:
        """
        Find the profit-maximizing charge/discharge schedule.
        
        THE ALGORITHM (simple but optimal for single-cycle):
        
        1. Calculate how many hours we need to charge/discharge
           - Based on battery capacity and power rating
           
        2. Sort hours by price (lowest to highest)
        
        3. Pick cheapest N hours to charge
        
        4. Pick most expensive N hours to discharge
        
        5. Verify it's profitable after efficiency losses
        
        Returns None if not profitable, otherwise returns schedule dict.
        """
        
        usable_capacity_mwh = config.capacity_mwh * (config.max_soc - config.min_soc) / 100
        hours_needed = int(usable_capacity_mwh / config.power_mw)
        
        # Need at least 1 hour each for charge and discharge
        if hours_needed < 1:
            logger.warning("Battery too small for hourly arbitrage")
            return None
        
        # Can't trade if we don't have enough hours with prices
        if len(hours_with_prices) < hours_needed * 2:
            logger.warning(f"Only {len(hours_with_prices)} hours with prices, need {hours_needed * 2}")
            return None
        
        # --- Sort by price ---
        sorted_by_price = sorted(hours_with_prices, key=lambda x: x['price'])
        
        # --- Select charge hours (cheapest) ---
        charge_hours = sorted_by_price[:hours_needed]
        
        # --- Select discharge hours (most expensive) ---
        discharge_hours = sorted_by_price[-hours_needed:]
        
        # --- Check profitability ---
        #
        # For arbitrage to be profitable:
        #   Revenue from selling > Cost of buying + Efficiency losses
        #
        # With efficiency η (e.g., 0.87):
        #   - We buy X MWh at avg_charge_price
        #   - We sell X × η MWh at avg_discharge_price
        #   
        # Profit = (X × η × avg_discharge) - (X × avg_charge)
        # Profit = X × (η × avg_discharge - avg_charge)
        #
        # Profitable when: η × avg_discharge > avg_charge
        # Or: avg_discharge > avg_charge / η
        
        avg_charge_price = sum(h['price'] for h in charge_hours) / len(charge_hours)
        avg_discharge_price = sum(h['price'] for h in discharge_hours) / len(discharge_hours)
        
        # Minimum discharge price needed to break even
        breakeven_discharge = avg_charge_price / config.efficiency
        
        # Add a small margin (€2/MWh) to avoid trading for negligible profit
        min_profitable_discharge = breakeven_discharge + 2.0
        
        if avg_discharge_price < min_profitable_discharge:
            logger.info(
                f"Not profitable: discharge €{avg_discharge_price:.2f} < "
                f"required €{min_profitable_discharge:.2f}"
            )
            return None
        
        # --- We have a profitable schedule! ---
        return {
            'charge_hours': charge_hours,
            'discharge_hours': discharge_hours,
            'hours_needed': hours_needed,
            'avg_charge_price': avg_charge_price,
            'avg_discharge_price': avg_discharge_price,
            'expected_profit_per_mwh': avg_discharge_price * config.efficiency - avg_charge_price
        }
    
    # =========================================================================
    # STEP 4: Build hourly decisions
    # =========================================================================
    
    @staticmethod
    def _build_decisions(
        hourly_data: List[Dict], 
        schedule: Dict, 
        config
    ) -> List[Dict]:
        """
        Convert optimal schedule into hour-by-hour decisions.
        
        This creates the detailed output showing what happens each hour:
        - What action to take (CHARGE/DISCHARGE/HOLD)
        - Energy transferred
        - Cost/revenue
        - State of charge before/after
        """
        
        # Create sets of hour indices for quick lookup
        charge_indices = {h['index'] for h in schedule['charge_hours']}
        discharge_indices = {h['index'] for h in schedule['discharge_hours']}
        
        # Sort charge/discharge hours chronologically for proper SoC tracking
        charge_hours_sorted = sorted(schedule['charge_hours'], key=lambda x: x['hour'])
        discharge_hours_sorted = sorted(schedule['discharge_hours'], key=lambda x: x['hour'])
        
        # Track state of charge through the day
        current_soc = config.min_soc  # Start at minimum
        
        decisions = []
        
        for i, hour in enumerate(hourly_data):
            price = hour.get('price', 0)
            
            if i in charge_indices:
                # CHARGING
                energy_mwh = config.power_mw  # Charge at full power for 1 hour
                cost = energy_mwh * price      # Cost to buy energy
                soc_increase = (energy_mwh / config.capacity_mwh) * 100
                new_soc = min(current_soc + soc_increase, config.max_soc)
                
                decision = {
                    'hour': hour.get('hour'),
                    'action': 'CHARGE',
                    'price': round(price, 2),
                    'energy_mwh': round(energy_mwh, 1),
                    'cost_eur': round(cost, 2),  # Positive = we pay
                    'soc_before': round(current_soc, 1),
                    'soc_after': round(new_soc, 1),
                    'reasoning': [f'✓ Optimal charge hour (€{price:.2f}/MWh)']
                }
                current_soc = new_soc
                
            elif i in discharge_indices:
                # DISCHARGING
                # Energy we can sell = power × efficiency
                energy_out = config.power_mw * config.efficiency
                revenue = energy_out * price  # Revenue from selling
                
                # Battery drains faster than we sell (efficiency loss)
                battery_drain = config.power_mw  # Full power draw from battery
                soc_decrease = (battery_drain / config.capacity_mwh) * 100
                new_soc = max(current_soc - soc_decrease, config.min_soc)
                
                decision = {
                    'hour': hour.get('hour'),
                    'action': 'DISCHARGE',
                    'price': round(price, 2),
                    'energy_mwh': round(energy_out, 1),  # Energy sold (after efficiency)
                    'cost_eur': round(-revenue, 2),  # Negative = we earn
                    'soc_before': round(current_soc, 1),
                    'soc_after': round(new_soc, 1),
                    'reasoning': [f'✓ Optimal discharge hour (€{price:.2f}/MWh)']
                }
                current_soc = new_soc
                
            else:
                # HOLD
                decision = {
                    'hour': hour.get('hour'),
                    'action': 'HOLD',
                    'price': round(price, 2) if price else 0,
                    'energy_mwh': 0,
                    'cost_eur': 0,
                    'soc_before': round(current_soc, 1),
                    'soc_after': round(current_soc, 1),
                    'reasoning': ['⚪ Not optimal for trading']
                }
            
            decisions.append(decision)
        
        return decisions
    
    @staticmethod
    def _build_hold_decisions(hourly_data: List[Dict], config) -> List[Dict]:
        """Build all-HOLD decisions when no profitable arbitrage exists."""
        return [
            {
                'hour': hour.get('hour'),
                'action': 'HOLD',
                'price': round(hour.get('price', 0), 2) if hour.get('price') else 0,
                'energy_mwh': 0,
                'cost_eur': 0,
                'soc_before': config.min_soc,
                'soc_after': config.min_soc,
                'reasoning': ['⚪ No profitable arbitrage opportunity']
            }
            for hour in hourly_data
        ]
    
    # =========================================================================
    # STEP 5: Calculate performance
    # =========================================================================
    
    @staticmethod
    def _calculate_performance(decisions: List[Dict], config) -> Dict:
        """
        Calculate daily performance metrics.
        
        Simple arithmetic - no magic:
        - Sum up all charging costs
        - Sum up all discharging revenues
        - Profit = Revenue - Cost
        """
        charges = [d for d in decisions if d['action'] == 'CHARGE']
        discharges = [d for d in decisions if d['action'] == 'DISCHARGE']
        
        # Financial metrics
        total_charge_cost = sum(d['cost_eur'] for d in charges)
        total_discharge_revenue = sum(-d['cost_eur'] for d in discharges)  # cost_eur is negative for discharge
        gross_profit = total_discharge_revenue - total_charge_cost
        
        # Energy metrics
        total_charged = sum(d['energy_mwh'] for d in charges)
        total_discharged = sum(d['energy_mwh'] for d in discharges)
        
        # Cycles (how many times we used the full usable capacity)
        usable_capacity = config.capacity_mwh * (config.max_soc - config.min_soc) / 100
        cycles = total_discharged / usable_capacity if usable_capacity > 0 else 0
        
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
    
    @staticmethod
    def _empty_performance() -> Dict:
        """Return zeroed performance for days with no trading."""
        return {
            'gross_profit_eur': 0,
            'revenue_eur': 0,
            'cost_eur': 0,
            'energy_charged_mwh': 0,
            'energy_discharged_mwh': 0,
            'avg_charge_price': 0,
            'avg_discharge_price': 0,
            'cycles_completed': 0,
            'charge_hours': 0,
            'discharge_hours': 0,
            'utilization_pct': 0
        }