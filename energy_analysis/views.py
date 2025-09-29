# views.py
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from .models import EnergyData, DailyEnergySummary
from .serializers import EnergyDataSerializer
from rest_framework.decorators import action
from .services.daily_summary_service import DailySummaryService
from .utils.data_quality import EnergyDataValidator
import logging

logger = logging.getLogger(__name__)

class EnergyDataViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnergyDataSerializer
    
    def get_queryset(self):
        queryset = EnergyData.objects.all()
        
        # Filter by date if provided
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(timestamp__date=date)
        
        # Filter by indicators (VRE + Demand)
        indicators = self.request.query_params.get('indicators', '1161,1159,1293')
        indicator_list = [int(x) for x in indicators.split(',')]
        queryset = queryset.filter(indicator__indicator_id__in=indicator_list)
        
        return queryset.order_by('timestamp')
    
    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """
        Get chart data for any date - uses DailyEnergySummary service
        Handles both 2024 database data and live ESIOS data
        """
        date = request.query_params.get('date', '2024-04-15')
        
        try:
            # Single entry point - service handles routing to DB or ESIOS
            summary, created = DailySummaryService.get_or_create_summary(date)
            
            # Build daily insights from summary fields
            daily_insights = {
                'peak_vre_pct': summary.peak_vre_penetration,
                'peak_vre_hour': summary.peak_vre_hour.strftime('%H:%M'),
                'avg_vre_pct': round(sum(h['vre_pct'] for h in summary.hourly_data_json['hourly_data']) / len(summary.hourly_data_json['hourly_data']), 1),
                'peak_demand': max(h['demand'] for h in summary.hourly_data_json['hourly_data']),
                'peak_vre': max(h['vre_total'] for h in summary.hourly_data_json['hourly_data']),
                'min_vre_pct': min(h['vre_pct'] for h in summary.hourly_data_json['hourly_data']),
                'min_vre_hour': min(summary.hourly_data_json['hourly_data'], key=lambda x: x['vre_pct'])['hour'],
                
                # Flexibility insights from your new metrics
                'optimal_shift_amount': summary.shiftable_energy_gwh,
                'shift_from_hour': summary.peak_demand_hour.strftime('%H:%M'),
                'shift_to_hour': summary.peak_vre_hour.strftime('%H:%M'),
                'shift_from_vre_pct': self._get_vre_pct_at_hour(summary.hourly_data_json['hourly_data'], summary.peak_demand_hour),
                'shift_to_vre_pct': summary.peak_vre_penetration,
                'high_vre_window_hours': summary.sustained_high_vre_hours,
                'flexibility_window_start': summary.flexibility_window_start.strftime('%H:%M') if summary.flexibility_window_start else None,
                'flexibility_window_end': summary.flexibility_window_end.strftime('%H:%M') if summary.flexibility_window_end else None,
                
                # New analytics insights
                'max_ramp_gw': summary.max_netload_ramp_gw,
                'ramp_window': f"{summary.ramp_window_start.strftime('%H:%M')}-{summary.ramp_window_end.strftime('%H:%M')}",
                'load_balancing_gap_hours': summary.load_balancing_gap_hours
            }
            data_quality = EnergyDataValidator.assess_hourly_data_quality(summary.hourly_data_json['hourly_data'])
            
            return Response({
                'date': date,
                'hourly_data': summary.hourly_data_json['hourly_data'],
                'daily_insights': daily_insights,
                'data_quality': data_quality,
                'was_cached': not created,
                'data_source': summary.data_source
            })
            
        except ValueError as e:
            logger.error(f"Chart data validation error for {date}: {e}")
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Chart data error for {date}: {e}")
            return Response({'error': 'Failed to fetch energy data'}, status=500)
    
    def _get_vre_pct_at_hour(self, hourly_data, target_time):
        """Helper to get VRE percentage at specific hour"""
        target_hour_str = target_time.strftime('%H:%M')
        for hour_data in hourly_data:
            if hour_data['hour'] == target_hour_str:
                return hour_data['vre_pct']
        return 0