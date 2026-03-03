# services/gridstatus_service.py
"""
Service for fetching US ISO data via gridstatus library.
Normalizes data to match the existing Spain/ESIOS format for frontend compatibility.
"""
from gridstatus import CAISO
import pandas as pd
from datetime import datetime
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class GridStatusService:
    """
    Fetches and normalizes CAISO data to match ESIOS format.
    
    Output format matches EsiosService so frontend works without changes.
    """
    
    def __init__(self, iso: str = 'caiso'):
        self.iso_name = iso.lower()
        if self.iso_name == 'caiso':
            self.client = CAISO()
        else:
            raise ValueError(f"Unsupported ISO: {iso}. Currently only 'caiso' supported.")
    
    # =========================================================================
    # GENERATION / LOAD DATA (for VRE & Net Load charts)
    # =========================================================================
    
    def fetch_day_data(self, date_string: str) -> Optional[Dict]:
        """Fetch generation + load data, compute insights."""
        try:
            logger.info(f"Fetching CAISO generation data for {date_string}")
            
            fuel_mix = self.client.get_fuel_mix(date=date_string)
            load = self.client.get_load(date=date_string)
            prices = self._fetch_prices(date_string)
            
            if fuel_mix.empty or load.empty:
                logger.warning(f"No data returned for {date_string}")
                return None
            
            hourly_data = self._aggregate_generation_to_hourly(fuel_mix, load, prices)
            
            # Compute daily insights from hourly data
            daily_insights = self._compute_daily_insights(hourly_data)
            
            return {
                'date': date_string,
                'hourly_data': hourly_data,
                'daily_insights': daily_insights  # <-- This was missing!
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch CAISO day data for {date_string}: {e}")
            return None
    
    def _fetch_prices(self, date_string: str) -> Optional[pd.DataFrame]:
        """Fetch LMP prices, return None if unavailable."""
        try:
            prices = self.client.get_lmp(date=date_string, market="REAL_TIME_5_MIN")
            return prices
        except Exception as e:
            logger.warning(f"Could not fetch prices for {date_string}: {e}")
            return None
    
    def _aggregate_generation_to_hourly(
        self, 
        fuel_mix: pd.DataFrame, 
        load: pd.DataFrame,
        prices: Optional[pd.DataFrame]
    ) -> List[Dict]:
        """Aggregate 5-min data to hourly, matching ESIOS format."""
        
        fuel_mix = fuel_mix.copy()
        load = load.copy()
        
        # Floor to hour (lowercase 'h' for newer pandas)
        fuel_mix['hour'] = fuel_mix['Interval Start'].dt.floor('h')
        load['hour'] = load['Interval Start'].dt.floor('h')
        
        # Aggregate generation (mean MW per hour)
        fuel_hourly = fuel_mix.groupby('hour').agg({
            'Solar': 'mean',
            'Wind': 'mean'
        }).reset_index()
        
        # Aggregate load (mean MW per hour)
        load_hourly = load.groupby('hour').agg({
            'Load': 'mean'
        }).reset_index()
        
        # Aggregate prices if available (mean across all hubs)
        price_dict = {}
        if prices is not None and not prices.empty:
            prices = prices.copy()
            prices['hour'] = prices['Interval Start'].dt.floor('h')
            price_hourly = prices.groupby('hour')['LMP'].mean()
            price_dict = price_hourly.to_dict()
        
        # Merge generation and load
        merged = fuel_hourly.merge(load_hourly, on='hour', how='outer')
        
        # Build output
        hourly_data = []
        for _, row in merged.iterrows():
            hour_str = row['hour'].strftime('%H:00')
            
            # Convert MW to GW
            demand_gw = row['Load'] / 1000
            # Solar can be negative at night (grid consumption) - floor at 0
            solar_gw = max(0, row['Solar'] / 1000)
            wind_gw = row['Wind'] / 1000
            vre_total_gw = solar_gw + wind_gw
            net_load_gw = demand_gw - vre_total_gw
            
            # Percentages
            if demand_gw > 0:
                solar_pct = round((solar_gw / demand_gw) * 100, 1)
                wind_pct = round((wind_gw / demand_gw) * 100, 1)
                vre_pct = round((vre_total_gw / demand_gw) * 100, 1)
            else:
                solar_pct = wind_pct = vre_pct = 0
            
            # Price (USD/MWh for CAISO)
            price = round(price_dict.get(row['hour'], 0), 2)
            
            hourly_data.append({
                'hour': hour_str,
                'demand': round(demand_gw, 2),
                'solar': round(solar_gw, 2),
                'wind': round(wind_gw, 2),
                'vre_total': round(vre_total_gw, 2),
                'net_load': round(net_load_gw, 2),
                'solar_pct': solar_pct,
                'wind_pct': wind_pct,
                'vre_pct': vre_pct,
                'price': price
            })
        
        # Sort by hour
        hourly_data.sort(key=lambda x: x['hour'])
        return hourly_data
    
    def _compute_daily_insights(self, hourly_data: list) -> dict:
        """Compute daily insights from hourly data."""
        if not hourly_data:
            return {}
        
        # Peak VRE hour
        peak_vre_hour = max(hourly_data, key=lambda x: x['vre_pct'])
        min_vre_hour = min(hourly_data, key=lambda x: x['vre_pct'])
        peak_demand_hour = max(hourly_data, key=lambda x: x['demand'])
        
        # Calculate max ramp (biggest 2-hour net load swing)
        net_loads = [h['net_load'] for h in hourly_data]
        max_ramp = 0
        ramp_start_idx = 0
        for i in range(len(net_loads) - 2):
            ramp = abs(net_loads[i + 2] - net_loads[i])
            if ramp > max_ramp:
                max_ramp = ramp
                ramp_start_idx = i
        
        # High VRE hours (>70%)
        high_vre_hours = [h for h in hourly_data if h['vre_pct'] > 70]
        
        return {
            'peak_vre_pct': peak_vre_hour['vre_pct'],
            'peak_vre_hour': peak_vre_hour['hour'],
            'avg_vre_pct': round(sum(h['vre_pct'] for h in hourly_data) / len(hourly_data), 1),
            'peak_demand': max(h['demand'] for h in hourly_data),
            'peak_vre': max(h['vre_total'] for h in hourly_data),
            'min_vre_pct': min_vre_hour['vre_pct'],
            'min_vre_hour': min_vre_hour['hour'],
            
            # Flexibility insights
            'optimal_shift_amount': round(sum(h['vre_total'] for h in high_vre_hours) * 0.1, 2) if high_vre_hours else 0,
            'shift_from_hour': peak_demand_hour['hour'],
            'shift_to_hour': peak_vre_hour['hour'],
            'shift_from_vre_pct': peak_demand_hour['vre_pct'],
            'shift_to_vre_pct': peak_vre_hour['vre_pct'],
            'high_vre_window_hours': len(high_vre_hours),
            'flexibility_window_start': high_vre_hours[0]['hour'] if high_vre_hours else None,
            'flexibility_window_end': high_vre_hours[-1]['hour'] if high_vre_hours else None,
            
            # Ramp insights  
            'max_ramp_gw': round(max_ramp, 2),
            'ramp_window': f"{hourly_data[ramp_start_idx]['hour']}-{hourly_data[min(ramp_start_idx + 2, len(hourly_data) - 1)]['hour']}",
            'load_balancing_gap_hours': abs(
                int(peak_demand_hour['hour'].split(':')[0]) - 
                int(peak_vre_hour['hour'].split(':')[0])
            )
        }
    
    # =========================================================================
    # CURTAILMENT DATA
    # =========================================================================
    
    def fetch_curtailment_data(self, date_string: str) -> Optional[Dict]:
        """
        Fetch curtailment data with price overlay.
        Output matches Spain's DailyCurtailmentService format.
        
        Returns:
            {
                'date': '2024-06-20',
                'hourly_data': [
                    {
                        'hour': '00:00',
                        'curtailed_mwh': 0,
                        'spot_price': 34.50,
                        'revenue_lost': 0
                    },
                    ...
                ],
                'daily_insights': {
                    'total_curtailed_mwh': 1234.5,
                    'estimated_revenue_lost_usd': 45678.90,
                    'peak_curtailment_mwh': 234.5,
                    'peak_curtailment_hour': '13:00',
                    'curtailment_hours': 8,
                    'negative_price_hours': 2,
                    'negative_price_curtailed_mwh': 123.4
                },
                'curtailment_breakdown': {  # CAISO-specific extras
                    'by_reason': {'Local': 800.0, 'System': 434.5},
                    'by_fuel': {'Solar': 900.0, 'Wind': 334.5},
                    'by_type': {'Economic': 1000.0, 'SelfSchCut': 234.5}
                }
            }
        """
        try:
            logger.info(f"Fetching CAISO curtailment for {date_string}")
            
            # Fetch curtailment (hourly, sparse)
            curtailment = self.client.get_curtailment_legacy(date=date_string)
            
            # Fetch prices
            prices = self._fetch_prices(date_string)
            
            # Build hourly structure
            hourly_data = self._build_curtailment_hourly(curtailment, prices)
            
            # Calculate insights
            daily_insights = self._calculate_curtailment_insights(hourly_data)
            
            # CAISO-specific breakdown
            breakdown = self._get_curtailment_breakdown(curtailment)
            
            return {
                'date': date_string,
                'hourly_data': hourly_data,
                'daily_insights': daily_insights,
                'curtailment_breakdown': breakdown
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch CAISO curtailment for {date_string}: {e}")
            return None
    
    def _build_curtailment_hourly(
        self, 
        curtailment: pd.DataFrame, 
        prices: Optional[pd.DataFrame]
    ) -> List[Dict]:
        """Build 24-hour curtailment array matching Spain format."""
        
        # Aggregate prices to hourly
        price_dict = {}
        if prices is not None and not prices.empty:
            prices = prices.copy()
            prices['hour'] = prices['Interval Start'].dt.floor('h')
            price_hourly = prices.groupby('hour')['LMP'].mean()
            # Convert to hour string keys
            price_dict = {k.strftime('%H:00'): v for k, v in price_hourly.items()}
        
        # Aggregate curtailment by hour
        curtail_dict = {}
        if curtailment is not None and not curtailment.empty:
            curtailment = curtailment.copy()
            # CRITICAL: Convert string to numeric!
            curtailment['Curtailment (MWh)'] = pd.to_numeric(
                curtailment['Curtailment (MWh)'], errors='coerce'
            ).fillna(0)
            
            curtailment['hour'] = curtailment['Interval Start'].dt.floor('h')
            curtail_hourly = curtailment.groupby('hour')['Curtailment (MWh)'].sum()
            curtail_dict = {k.strftime('%H:00'): v for k, v in curtail_hourly.items()}
        
        # Build 24-hour structure
        hourly_data = []
        for h in range(24):
            hour_str = f'{h:02d}:00'
            curtailed = curtail_dict.get(hour_str, 0)
            price = price_dict.get(hour_str, 0)
            
            # Revenue lost only for positive prices
            revenue_lost = curtailed * price if price > 0 else 0
            
            hourly_data.append({
                'hour': hour_str,
                'curtailed_mwh': round(float(curtailed), 1),
                'spot_price': round(float(price), 2),
                'revenue_lost': round(float(revenue_lost), 2)
            })
        
        return hourly_data
    
    def _calculate_curtailment_insights(self, hourly_data: List[Dict]) -> Dict:
        """Calculate daily summary metrics."""
        
        total_curtailed = sum(h['curtailed_mwh'] for h in hourly_data)
        total_revenue_lost = sum(h['revenue_lost'] for h in hourly_data)
        
        # Peak hour
        peak_hour = max(hourly_data, key=lambda x: x['curtailed_mwh'])
        
        # Counts
        curtailment_hours = sum(1 for h in hourly_data if h['curtailed_mwh'] > 0)
        negative_price_hours = sum(1 for h in hourly_data if h['spot_price'] < 0)
        negative_price_curtailed = sum(
            h['curtailed_mwh'] for h in hourly_data if h['spot_price'] < 0
        )
        
        return {
            'total_curtailed_mwh': round(total_curtailed, 1),
            'estimated_revenue_lost_usd': round(total_revenue_lost, 2),
            'peak_curtailment_mwh': round(peak_hour['curtailed_mwh'], 1),
            'peak_curtailment_hour': peak_hour['hour'],
            'curtailment_hours': curtailment_hours,
            'negative_price_hours': negative_price_hours,
            'negative_price_curtailed_mwh': round(negative_price_curtailed, 1)
        }
    
    def _get_curtailment_breakdown(self, curtailment: pd.DataFrame) -> Dict:
        """
        CAISO-specific breakdown by reason, fuel, and type.
        """
        if curtailment is None or curtailment.empty:
            return {'by_reason': {}, 'by_fuel': {}, 'by_type': {}}
        
        curtailment = curtailment.copy()
        # CRITICAL: Convert string to numeric!
        curtailment['Curtailment (MWh)'] = pd.to_numeric(
            curtailment['Curtailment (MWh)'], errors='coerce'
        ).fillna(0)
        
        # By reason (Local = transmission, System = oversupply)
        by_reason = curtailment.groupby('Curtailment Reason')['Curtailment (MWh)'].sum().to_dict()
        
        # By fuel (Solar vs Wind)
        by_fuel = curtailment.groupby('Fuel Type')['Curtailment (MWh)'].sum().to_dict()
        
        # By type (Economic vs SelfSchCut)
        by_type = curtailment.groupby('Curtailment Type')['Curtailment (MWh)'].sum().to_dict()
        
        return {
            'by_reason': {k: round(v, 1) for k, v in by_reason.items()},
            'by_fuel': {k: round(v, 1) for k, v in by_fuel.items()},
            'by_type': {k: round(v, 1) for k, v in by_type.items()}
        }