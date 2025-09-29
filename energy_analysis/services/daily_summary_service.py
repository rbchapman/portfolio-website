from datetime import datetime, timedelta
from django.db.models import Q
import logging
from ..models import DailyEnergySummary, EnergyData
from ..services.esios_service import EsiosService
from ..utils.energy_calculations import EnergyMetricsCalculator

logger = logging.getLogger(__name__)


class DailySummaryService:
    """
    Service for creating and managing DailyEnergySummary records
    Handles both 2024 database data and ESIOS API data
    """
    
    @classmethod
    def get_or_create_summary(cls, date_str):
        """
        Main entry point - get existing summary or create new one
        Returns: (DailyEnergySummary instance, created: bool)
        """
        try:
            date_obj = datetime.fromisoformat(date_str).date()
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")
        
        # Try to get existing summary
        try:
            summary = DailyEnergySummary.objects.get(date=date_obj)
            return summary, False
        except DailyEnergySummary.DoesNotExist:
            # Create new summary
            logger.info(f"Creating new DailyEnergySummary for {date_obj}")
            summary = cls._create_new_summary(date_obj)
            return summary, True
    
    @classmethod
    def _create_new_summary(cls, date_obj):
        """Route to appropriate data source based on year"""
        if date_obj.year == 2024:
            return cls._create_from_database(date_obj)
        else:
            return cls._create_from_esios(date_obj)
    
    @classmethod
    def _create_from_database(cls, date_obj):
        """Create summary from 2024 database data"""
        # Get hourly data for the three main indicators
        energy_data = EnergyData.objects.filter(
            timestamp__date=date_obj,
            indicator__indicator_id__in=[1161, 1159, 1293]  # Solar, Wind, Demand
        ).select_related('indicator').order_by('timestamp')
        
        if not energy_data.exists():
            raise ValueError(f"No energy data found for {date_obj}")
        
        # Transform to hourly format
        hourly_data = cls._transform_db_to_hourly(energy_data)
        
        # Calculate all metrics
        metrics = EnergyMetricsCalculator.calculate_all_metrics(hourly_data)
        
        # Create and save summary
        summary = DailyEnergySummary.objects.create(
            date=date_obj,
            data_source='database',
            hourly_data_json={'hourly_data': hourly_data},
            **metrics
        )
        
        logger.info(f"Created DB summary for {date_obj}: Peak VRE {metrics['peak_vre_penetration']}%")
        return summary
    
    @classmethod
    def _create_from_esios(cls, date_obj):
        """Create summary from ESIOS API data using existing EsiosService"""
        try:
            esios_service = EsiosService()
            esios_response = esios_service.fetch_day_data(date_obj.isoformat())
            
            if not esios_response or not esios_response.get('hourly_data'):
                raise ValueError(f"No ESIOS data available for {date_obj}")
            
            # Your EsiosService already returns perfect hourly format
            hourly_data = esios_response['hourly_data']
            
            # Validate data quality before calculations
            EnergyMetricsCalculator.validate_hourly_data(hourly_data)
            
            # Calculate all metrics
            metrics = EnergyMetricsCalculator.calculate_all_metrics(hourly_data)
            
            # Create and save summary
            summary = DailyEnergySummary.objects.create(
                date=date_obj,
                data_source='esios',
                hourly_data_json=esios_response,  # Store full ESIOS response
                **metrics
            )
            
            logger.info(f"Created ESIOS summary for {date_obj}: Peak VRE {metrics['peak_vre_penetration']}%")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to create ESIOS summary for {date_obj}: {e}")
            raise
    
    @classmethod
    def _transform_db_to_hourly(cls, energy_data):
        """Transform database EnergyData to hourly chart format"""
        hourly_dict = {}
        
        # Group by hour
        for item in energy_data:
            hour_key = item.timestamp.strftime('%H:%M')
            
            if hour_key not in hourly_dict:
                hourly_dict[hour_key] = {
                    'hour': hour_key,
                    'demand': 0,
                    'solar': 0,
                    'wind': 0
                }
            
            # Convert MW to GW and assign to appropriate field
            value_gw = round(item.value / 1000, 2)
            
            if item.indicator.indicator_id == 1293:  # Demand
                hourly_dict[hour_key]['demand'] = value_gw
            elif item.indicator.indicator_id == 1161:  # Solar
                hourly_dict[hour_key]['solar'] = value_gw
            elif item.indicator.indicator_id == 1159:  # Wind
                hourly_dict[hour_key]['wind'] = value_gw
        
        # Calculate derived fields and sort
        hourly_data = []
        for hour_data in sorted(hourly_dict.values(), key=lambda x: x['hour']):
            # Add calculated fields
            hour_data['vre_total'] = round(hour_data['solar'] + hour_data['wind'], 2)
            
            if hour_data['demand'] > 0:
                hour_data['solar_pct'] = round((hour_data['solar'] / hour_data['demand']) * 100, 1)
                hour_data['wind_pct'] = round((hour_data['wind'] / hour_data['demand']) * 100, 1)
                hour_data['vre_pct'] = round((hour_data['vre_total'] / hour_data['demand']) * 100, 1)
            else:
                hour_data['solar_pct'] = 0
                hour_data['wind_pct'] = 0
                hour_data['vre_pct'] = 0
            
            hourly_data.append(hour_data)
        
        return hourly_data
    
    @classmethod
    def backfill_2024_summaries(cls, start_date=None, end_date=None):
        """
        Management command helper to backfill all 2024 data
        """
        if not start_date:
            start_date = datetime(2024, 1, 1).date()
        if not end_date:
            end_date = datetime(2024, 12, 31).date()
        
        current_date = start_date
        created_count = 0
        skipped_count = 0
        
        while current_date <= end_date:
            try:
                # Check if already exists
                if DailyEnergySummary.objects.filter(date=current_date).exists():
                    skipped_count += 1
                else:
                    cls._create_from_database(current_date)
                    created_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to create summary for {current_date}: {e}")
            
            current_date += timedelta(days=1)
        
        logger.info(f"Backfill complete: {created_count} created, {skipped_count} skipped")
        return created_count, skipped_count