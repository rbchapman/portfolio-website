from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from .models import EnergyData
from .serializers import EnergyDataSerializer
from rest_framework.decorators import action

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
        if sorted_hourly_data:
            vre_percentages = [hour['vre_pct'] for hour in sorted_hourly_data]
            demand_values = [hour['demand'] for hour in sorted_hourly_data]
            vre_values = [hour['vre_total'] for hour in sorted_hourly_data]
            
            # Find peak hours for demand shift analysis
            peak_vre_index = vre_percentages.index(max(vre_percentages))
            peak_demand_index = demand_values.index(max(demand_values))
            min_vre_index = vre_percentages.index(min(vre_percentages))
            
            peak_vre_hour_data = sorted_hourly_data[peak_vre_index]
            peak_demand_hour_data = sorted_hourly_data[peak_demand_index]
            min_vre_hour_data = sorted_hourly_data[min_vre_index]
            
            # Calculate demand shift opportunity
            # Conservative estimate: 10% of peak demand could potentially be shifted
            demand_at_peak = peak_demand_hour_data['demand']
            vre_available_at_peak = peak_vre_hour_data['vre_total']
            shift_potential = round(min(demand_at_peak * 0.1, vre_available_at_peak * 0.15), 1)
            
            # Find high VRE window (consecutive hours above average VRE penetration)
            avg_vre_pct = sum(vre_percentages) / len(vre_percentages)
            high_vre_hours = [hour for hour, pct in zip(sorted_hourly_data, vre_percentages) if pct > avg_vre_pct]
            
            daily_insights = {
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
        else:
            daily_insights = {}
        
        return Response({
            'date': date,
            'hourly_data': sorted_hourly_data,
            'daily_insights': daily_insights
        })