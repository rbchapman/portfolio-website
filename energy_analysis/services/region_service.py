# services/region_service.py
"""
Simple routing layer - picks the right service per region.
Keeps views clean, existing services untouched.
"""
import logging

logger = logging.getLogger(__name__)


class RegionService:
    
    SUPPORTED_REGIONS = ['california', 'spain']
    
    @classmethod
    def get_chart_data(cls, region: str, date: str) -> dict:
        """
        Returns normalized chart data for any region.
        Same output shape regardless of source.
        """
        if region == 'california':
            return cls._get_california_data(date)
        else:
            return cls._get_spain_data(date)
    
    @classmethod
    def _get_spain_data(cls, date: str) -> dict:
        """Use existing DailySummaryService"""
        from .daily_summary_service import DailySummaryService
        
        summary, created = DailySummaryService.get_or_create_summary(date)
        hourly_data = summary.hourly_data_json['hourly_data']
        
        daily_insights = {
            'peak_vre_pct': summary.peak_vre_penetration,
            'peak_vre_hour': summary.peak_vre_hour.strftime('%H:%M'),
            'avg_vre_pct': round(sum(h['vre_pct'] for h in hourly_data) / len(hourly_data), 1),
            'peak_demand': max(h['demand'] for h in hourly_data),
            'peak_vre': max(h['vre_total'] for h in hourly_data),
            'min_vre_pct': min(h['vre_pct'] for h in hourly_data),
            'min_vre_hour': min(hourly_data, key=lambda x: x['vre_pct'])['hour'],
            'optimal_shift_amount': summary.shiftable_energy_gwh,
            'shift_from_hour': summary.peak_demand_hour.strftime('%H:%M'),
            'shift_to_hour': summary.peak_vre_hour.strftime('%H:%M'),
            'shift_from_vre_pct': cls._get_vre_pct_at_hour(hourly_data, summary.peak_demand_hour),
            'shift_to_vre_pct': summary.peak_vre_penetration,
            'high_vre_window_hours': summary.sustained_high_vre_hours,
            'flexibility_window_start': summary.flexibility_window_start.strftime('%H:%M') if summary.flexibility_window_start else None,
            'flexibility_window_end': summary.flexibility_window_end.strftime('%H:%M') if summary.flexibility_window_end else None,
            'max_ramp_gw': summary.max_netload_ramp_gw,
            'ramp_window': f"{summary.ramp_window_start.strftime('%H:%M')}-{summary.ramp_window_end.strftime('%H:%M')}",
            'load_balancing_gap_hours': summary.load_balancing_gap_hours
        }
        
        return {
            'date': date,
            'hourly_data': hourly_data,
            'daily_insights': daily_insights,
            'data_source': summary.data_source,
            'was_cached': not created
        }
    
    @classmethod
    @classmethod
    def _get_california_data(cls, date: str) -> dict:
        """Use GridStatusService for CAISO, with DB caching"""
        from ..models import DailyEnergySummary
        from datetime import datetime
        
        date_obj = datetime.fromisoformat(date).date()
        
        # Check cache first
        try:
            summary = DailyEnergySummary.objects.get(date=date_obj, data_source='caiso')
            return {
                'date': date,
                'hourly_data': summary.hourly_data_json['hourly_data'],
                'daily_insights': summary.hourly_data_json.get('daily_insights', {}),
                'data_source': 'caiso',
                'was_cached': True
            }
        except DailyEnergySummary.DoesNotExist:
            pass
        
        # Fetch live
        from .gridstatus_service import GridStatusService
        
        svc = GridStatusService('caiso')
        data = svc.fetch_day_data(date)
        
        if data is None:
            raise ValueError(f"No CAISO data available for {date}")
        
        return {
            'date': date,
            'hourly_data': data['hourly_data'],
            'daily_insights': data['daily_insights'],
            'data_source': 'caiso',
            'was_cached': False
        }
    
    @classmethod
    def get_curtailment_data(cls, region: str, date: str) -> dict:
        """Returns normalized curtailment data for any region."""
        if region == 'california':
            return cls._get_california_curtailment(date)
        else:
            return cls._get_spain_curtailment(date)
    
    @classmethod
    def _get_spain_curtailment(cls, date: str) -> dict:
        """Use existing DailyCurtailmentService"""
        from .daily_curtailment_service import DailyCurtailmentService
        
        summary, created = DailyCurtailmentService.get_or_create_summary(date)
        hourly = summary.hourly_data_json['hourly_data']
        
        return {
            'date': date,
            'hourly_data': hourly,
            'daily_insights': {
                'total_curtailed_mwh': summary.total_curtailed_mwh,
                'estimated_revenue_lost': summary.estimated_revenue_lost_eur,
                'peak_curtailment_mwh': summary.peak_curtailment_mwh,
                'peak_curtailment_hour': summary.peak_curtailment_hour.strftime('%H:%M'),
                'curtailment_hours': sum(1 for h in hourly if h['curtailed_mwh'] > 0),
                'negative_price_hours': sum(1 for h in hourly if h['spot_price'] < 0),
                'negative_price_curtailed_mwh': round(sum(h['curtailed_mwh'] for h in hourly if h['spot_price'] < 0), 1),
            },
            'curtailment_breakdown': {},
            'was_cached': not created
        }
    
    @classmethod  
    def _get_california_curtailment(cls, date: str) -> dict:
        """Use GridStatusService for CAISO curtailment"""
        from .gridstatus_service import GridStatusService
        
        svc = GridStatusService('caiso')
        data = svc.fetch_curtailment_data(date)
        
        if data is None:
            raise ValueError(f"No CAISO curtailment data available for {date}")
        
        return {
            'date': date,
            'hourly_data': data['hourly_data'],
            'daily_insights': data['daily_insights'],
            'curtailment_breakdown': data.get('curtailment_breakdown', {}),
            'was_cached': False
        }
    
    @staticmethod
    def _get_vre_pct_at_hour(hourly_data, target_time):
        """Helper to get VRE percentage at specific hour"""
        target_hour_str = target_time.strftime('%H:%M')
        for hour_data in hourly_data:
            if hour_data['hour'] == target_hour_str:
                return hour_data['vre_pct']
        return 0