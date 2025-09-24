from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from .models import EnergyData
from .serializers import EnergyDataSerializer
from rest_framework.decorators import action
from .services.esios_service import EsiosService
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
        date = request.query_params.get('date', '2024-04-15')
        
        # Route based on year
        try:
            target_year = datetime.fromisoformat(date).year
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)
        
        if target_year == 2024:
            return self._get_database_chart_data(date)
        else:
            return self._get_esios_chart_data(date)
    
    def _get_database_chart_data(self, date):
        """Original database logic for 2024 data"""
        # Get data for the three indicators
        data = EnergyData.objects.filter(
            timestamp__date=date,
            indicator__indicator_id__in=[1161, 1159, 1293]
        ).order_by('timestamp')
        
        # Group by hour
        hourly_data = []
        hours = {}
        
        for item in data:
            hour = item.timestamp.strftime('%H:%M')
            if hour not in hours:
                hours[hour] = {
                    'hour': hour, 
                    'demand': 0, 
                    'solar': 0, 
                    'wind': 0
                }
            
            # Convert MW to GW and assign to appropriate field
            if item.indicator.indicator_id == 1293:  # Demand
                hours[hour]['demand'] = round(item.value / 1000, 2)
            elif item.indicator.indicator_id == 1161:  # Solar
                hours[hour]['solar'] = round(item.value / 1000, 2)
            elif item.indicator.indicator_id == 1159:  # Wind
                hours[hour]['wind'] = round(item.value / 1000, 2)
        
        # Calculate derived values for each hour
        for hour_data in hours.values():
            # Total VRE generation
            hour_data['vre_total'] = round(hour_data['solar'] + hour_data['wind'], 2)
            
            # Calculate penetration percentages (avoid division by zero)
            if hour_data['demand'] > 0:
                hour_data['solar_pct'] = round((hour_data['solar'] / hour_data['demand']) * 100, 1)
                hour_data['wind_pct'] = round((hour_data['wind'] / hour_data['demand']) * 100, 1)
                hour_data['vre_pct'] = round((hour_data['vre_total'] / hour_data['demand']) * 100, 1)
            else:
                hour_data['solar_pct'] = 0
                hour_data['wind_pct'] = 0
                hour_data['vre_pct'] = 0
            
            hourly_data.append(hour_data)
        
        # Sort by hour
        sorted_hourly_data = sorted(hourly_data, key=lambda x: x['hour'])
        
        # Calculate daily insights
        daily_insights = self._calculate_daily_insights(sorted_hourly_data)
        
        # Assess data quality for database data too
        data_quality = EnergyDataValidator.assess_hourly_data_quality(sorted_hourly_data)
        
        return Response({
            'date': date,
            'hourly_data': sorted_hourly_data,
            'daily_insights': daily_insights,
            'data_quality': data_quality
        })
    
    def _get_esios_chart_data(self, date):
        """ESIOS API logic for non-2024 data"""
        try:
            service = EsiosService()
            esios_data = service.fetch_day_data(date)
            
            if not esios_data:
                return Response({'error': 'Failed to fetch data from ESIOS'}, status=500)
            
            # Convert ESIOS data to match database format
            hourly_data = []
            for hour_data in esios_data['hourly_data']:
                # Convert MW to GW and adjust hour format to match database
                converted_data = {
                    'hour': hour_data['hour'].replace(':00', ':00'),  # Keep as HH:00 for now
                    'demand': round(hour_data['demand'] / 1000, 2),  # MW -> GW
                    'solar': round(hour_data['solar'] / 1000, 2),    # MW -> GW  
                    'wind': round(hour_data['wind'] / 1000, 2),      # MW -> GW
                    'vre_total': round(hour_data['vre_total'] / 1000, 2),  # MW -> GW
                    'solar_pct': hour_data['solar_pct'],
                    'wind_pct': hour_data['wind_pct'], 
                    'vre_pct': hour_data['vre_pct']
                }
                hourly_data.append(converted_data)
            
            # Calculate daily insights using same logic
            daily_insights = self._calculate_daily_insights(hourly_data)
            
            # Assess data quality
            data_quality = EnergyDataValidator.assess_hourly_data_quality(hourly_data)
            
            return Response({
                'date': date,
                'hourly_data': hourly_data,
                'daily_insights': daily_insights,
                'data_quality': data_quality
            })
            
        except Exception as e:
            logger.error(f"ESIOS API error for {date}: {e}")
            return Response({'error': 'Failed to fetch energy data'}, status=500)
    
    def _calculate_daily_insights(self, hourly_data):
        """Calculate daily insights from hourly data - shared logic"""
        if not hourly_data:
            return {}
        
        vre_percentages = [hour['vre_pct'] for hour in hourly_data]
        demand_values = [hour['demand'] for hour in hourly_data]
        vre_values = [hour['vre_total'] for hour in hourly_data]
        
        # Find peak hours for demand shift analysis
        peak_vre_index = vre_percentages.index(max(vre_percentages))
        peak_demand_index = demand_values.index(max(demand_values))
        min_vre_index = vre_percentages.index(min(vre_percentages))
        
        peak_vre_hour_data = hourly_data[peak_vre_index]
        peak_demand_hour_data = hourly_data[peak_demand_index]
        min_vre_hour_data = hourly_data[min_vre_index]
        
        # Calculate demand shift opportunity
        # Conservative estimate: 10% of peak demand could potentially be shifted
        demand_at_peak = peak_demand_hour_data['demand']
        vre_available_at_peak = peak_vre_hour_data['vre_total']
        shift_potential = round(min(demand_at_peak * 0.1, vre_available_at_peak * 0.15), 1)
        
        # Find high VRE window (consecutive hours above average VRE penetration)
        avg_vre_pct = sum(vre_percentages) / len(vre_percentages)
        high_vre_hours = [hour for hour, pct in zip(hourly_data, vre_percentages) if pct > avg_vre_pct]
        
        return {
            'peak_vre_pct': max(vre_percentages),
            'peak_vre_hour': peak_vre_hour_data['hour'],
            'avg_vre_pct': round(avg_vre_pct, 1),
            'peak_demand': max(demand_values),
            'peak_vre': max(vre_values),
            'min_vre_pct': min(vre_percentages),
            'min_vre_hour': min_vre_hour_data['hour'],
            # Demand shift insights
            'optimal_shift_amount': shift_potential,
            'shift_from_hour': peak_demand_hour_data['hour'],
            'shift_to_hour': peak_vre_hour_data['hour'],
            'shift_from_vre_pct': peak_demand_hour_data['vre_pct'],
            'shift_to_vre_pct': peak_vre_hour_data['vre_pct'],
            'high_vre_window_hours': len(high_vre_hours),
            'flexibility_window_start': high_vre_hours[0]['hour'] if high_vre_hours else None,
            'flexibility_window_end': high_vre_hours[-1]['hour'] if high_vre_hours else None
        }