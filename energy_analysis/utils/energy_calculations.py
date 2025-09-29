from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)


class EnergyMetricsCalculator:
    """
    Pure calculation functions for energy metrics
    All methods are static and don't depend on Django models
    """
    
    @staticmethod
    def calculate_all_metrics(hourly_data):
        """
        Calculate all DailyEnergySummary metrics from hourly data
        
        Args:
            hourly_data: List of hourly energy data dictionaries
            Expected format: [{'hour': 'HH:MM', 'demand': float, 'solar': float, 'wind': float, 'vre_pct': float}, ...]
        
        Returns:
            dict: All calculated metrics for DailyEnergySummary
        """
        if not hourly_data:
            raise ValueError("No hourly data provided")
        
        # Extract key arrays for calculations
        vre_percentages = [hour['vre_pct'] for hour in hourly_data]
        demand_values = [hour['demand'] for hour in hourly_data]
        vre_values = [hour['vre_total'] for hour in hourly_data if 'vre_total' in hour]
        
        # If vre_total not in data, calculate it
        if not vre_values:
            vre_values = [hour['solar'] + hour['wind'] for hour in hourly_data]
        
        # Calculate individual metrics
        visibility_metrics = EnergyMetricsCalculator._calculate_visibility_metrics(hourly_data, vre_percentages)
        analytics_metrics = EnergyMetricsCalculator._calculate_analytics_metrics(hourly_data, demand_values, vre_values)
        flexibility_metrics = EnergyMetricsCalculator._calculate_flexibility_metrics(hourly_data, vre_percentages, demand_values)
        
        # Combine all metrics
        all_metrics = {
            **visibility_metrics,
            **analytics_metrics,
            **flexibility_metrics
        }
        
        logger.debug(f"Calculated metrics: Peak VRE {all_metrics['peak_vre_penetration']}%, "
                    f"Max ramp {all_metrics['max_netload_ramp_gw']}GW")
        
        return all_metrics
    
    @staticmethod
    def _calculate_visibility_metrics(hourly_data, vre_percentages):
        
        # Peak VRE penetration and timing
        peak_vre_pct = max(vre_percentages)
        peak_vre_index = vre_percentages.index(peak_vre_pct)
        peak_vre_hour_str = hourly_data[peak_vre_index]['hour']
        
        # Convert hour string to time object
        peak_vre_hour = datetime.strptime(peak_vre_hour_str, '%H:%M').time()
        
        # Sustained high VRE hours (>70%)
        sustained_high_vre_hours = sum(1 for pct in vre_percentages if pct > 70)
        
        return {
            'peak_vre_penetration': round(peak_vre_pct, 1),
            'peak_vre_hour': peak_vre_hour,
            'sustained_high_vre_hours': sustained_high_vre_hours
        }
    
    @staticmethod
    def _calculate_analytics_metrics(hourly_data, demand_values, vre_values):
        """Calculate Tatari-style analytics metrics"""
        
        # Calculate net load (demand - VRE) for each hour
        net_load = []
        for i, hour in enumerate(hourly_data):
            net_load_value = demand_values[i] - vre_values[i]
            net_load.append(net_load_value)
        
        # Find maximum 2-hour net load ramp
        max_ramp = 0
        ramp_start_idx = 0
        ramp_end_idx = 1
        
        for i in range(len(net_load) - 1):
            ramp = abs(net_load[i + 1] - net_load[i])
            if ramp > max_ramp:
                max_ramp = ramp
                ramp_start_idx = i
                ramp_end_idx = i + 1
        
        # Convert indices to time objects
        ramp_start_hour = datetime.strptime(hourly_data[ramp_start_idx]['hour'], '%H:%M').time()
        ramp_end_hour = datetime.strptime(hourly_data[ramp_end_idx]['hour'], '%H:%M').time()
        
        return {
            'max_netload_ramp_gw': round(max_ramp, 2),
            'ramp_window_start': ramp_start_hour,
            'ramp_window_end': ramp_end_hour
        }
    
    @staticmethod
    def _calculate_flexibility_metrics(hourly_data, vre_percentages, demand_values):
        """Calculate TIA-style flexibility metrics"""
        
        # Find peak demand and peak VRE hours
        peak_demand_idx = demand_values.index(max(demand_values))
        peak_vre_idx = vre_percentages.index(max(vre_percentages))
        
        peak_demand_hour = datetime.strptime(hourly_data[peak_demand_idx]['hour'], '%H:%M').time()
        peak_vre_hour = datetime.strptime(hourly_data[peak_vre_idx]['hour'], '%H:%M').time()
        
        # Calculate time gap between peaks (in hours)
        demand_hour_int = peak_demand_hour.hour
        vre_hour_int = peak_vre_hour.hour
        
        # Handle day wraparound
        if demand_hour_int >= vre_hour_int:
            gap_hours = demand_hour_int - vre_hour_int
        else:
            gap_hours = (24 - vre_hour_int) + demand_hour_int
        
        # Calculate shiftable energy (conservative estimate)
        # Energy available during high VRE hours that could be shifted to peak demand time
        avg_vre_pct = sum(vre_percentages) / len(vre_percentages)
        high_vre_hours = [hour for hour, pct in zip(hourly_data, vre_percentages) if pct > avg_vre_pct]
        
        # Estimate shiftable energy as 15% of excess VRE generation during high hours
        shiftable_energy = 0
        for hour in high_vre_hours:
            excess_vre = max(0, hour['vre_total'] - hour['demand'])
            shiftable_energy += excess_vre * 0.15  # Conservative 15% factor
        
        # Find flexibility window (consecutive high VRE hours)
        flexibility_window_start = None
        flexibility_window_end = None
        
        if high_vre_hours:
            flexibility_window_start = datetime.strptime(high_vre_hours[0]['hour'], '%H:%M').time()
            flexibility_window_end = datetime.strptime(high_vre_hours[-1]['hour'], '%H:%M').time()
        
        return {
            'load_balancing_gap_hours': gap_hours,
            'peak_demand_hour': peak_demand_hour,
            'shiftable_energy_gwh': round(shiftable_energy, 2),
            'flexibility_window_start': flexibility_window_start,
            'flexibility_window_end': flexibility_window_end
        }
    
    @staticmethod
    def calculate_daily_totals(hourly_data):
        """
        Calculate daily energy totals
        """
        daily_totals = {
            'daily_solar_gwh': sum(hour['solar'] for hour in hourly_data),
            'daily_wind_gwh': sum(hour['wind'] for hour in hourly_data),
            'daily_demand_gwh': sum(hour['demand'] for hour in hourly_data),
            'daily_vre_gwh': sum(hour.get('vre_total', hour['solar'] + hour['wind']) for hour in hourly_data)
        }
        
        return {k: round(v, 2) for k, v in daily_totals.items()}
    
    @staticmethod
    def validate_hourly_data(hourly_data):
        """
        Validate that hourly data has required fields and reasonable values
        """
        required_fields = ['hour', 'demand', 'solar', 'wind']
        
        for i, hour in enumerate(hourly_data):
            # Check required fields
            for field in required_fields:
                if field not in hour:
                    raise ValueError(f"Missing required field '{field}' in hour {i}")
            
            # Check for reasonable values
            if hour['demand'] < 0:
                logger.warning(f"Negative demand at {hour['hour']}: {hour['demand']}")
            
            if hour['solar'] < 0 or hour['wind'] < 0:
                logger.warning(f"Negative generation at {hour['hour']}")
        
        # Check we have 24 hours (or close to it)
        if len(hourly_data) < 20:
            logger.warning(f"Incomplete day data: only {len(hourly_data)} hours")
        
        return True