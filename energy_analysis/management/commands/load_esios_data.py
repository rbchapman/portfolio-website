# management/commands/load_esios_data.py
from django.core.management.base import BaseCommand
from energy_analysis.models import EnergyIndicator, EnergyData
import esios
from datetime import datetime, timedelta
import pandas as pd
import time


class Command(BaseCommand):
    help = 'Load ESIOS energy data into database for analysis'

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=str, help='Start date (YYYY-MM-DD)')
        parser.add_argument('end_date', type=str, help='End date (YYYY-MM-DD)')
        parser.add_argument('--indicator', type=int, default=1293, 
                          help='ESIOS indicator ID (default: 1293 - Demand)')
        parser.add_argument('--resolution', choices=['5min', 'hour'], default='hour',
                          help='Data resolution to load (default: hour)')
        parser.add_argument('--chunk-days', type=int, default=7,
                          help='Days per API chunk for reliability (default: 7)')

    def handle(self, *args, **options):
        # Parse arguments
        start_date = datetime.fromisoformat(options['start_date'])
        end_date = datetime.fromisoformat(options['end_date'])
        indicator_id = options['indicator']
        resolution = options['resolution']
        chunk_days = options['chunk_days']

        self.stdout.write(f"🔄 Loading ESIOS indicator {indicator_id} ({resolution}) from {start_date.date()} to {end_date.date()}")
        
        # Get or create indicator
        indicator_obj = self._get_or_create_indicator(indicator_id)
        if not indicator_obj:
            return  # Error already printed
            
        # Initialize ESIOS client
        try:
            client = esios.ESIOSClient()
            esios_indicator = client.endpoint('indicators').select(indicator_id)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to connect to ESIOS: {e}'))
            return

        # Process data in chunks
        total_created, total_updated = self._process_date_range(
            esios_indicator, indicator_obj, indicator_id, 
            start_date, end_date, chunk_days, resolution
        )

        # Summary
        self.stdout.write(self.style.SUCCESS(
            f'🎉 Complete! {total_created} created, {total_updated} updated'
        ))

    def _get_or_create_indicator(self, indicator_id):
        """Get existing indicator or create with basic info"""
        try:
            return EnergyIndicator.objects.get(esios_id=indicator_id)
        except EnergyIndicator.DoesNotExist:
            # Create with default values - can be updated later
            indicator_data = self._get_default_indicator_data(indicator_id)
            indicator_obj = EnergyIndicator.objects.create(**indicator_data)
            self.stdout.write(f"📝 Created new indicator: {indicator_obj.name}")
            return indicator_obj
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database error: {e}'))
            return None

    def _get_default_indicator_data(self, indicator_id):
        """Default indicator metadata for common ESIOS indicators"""
        defaults = {
            1293: {'name': 'Demanda real', 'short_name': 'Demand', 'type': 'demand', 'unit': 'MW'},
            1161: {'name': 'Generación Solar fotovoltaica', 'short_name': 'Solar PV', 'type': 'generation', 'unit': 'MW'},
            1159: {'name': 'Generación Eólica terrestre', 'short_name': 'Wind Onshore', 'type': 'generation', 'unit': 'MW'},
            600: {'name': 'Precio mercado SPOT Diario', 'short_name': 'Spot Price', 'type': 'price', 'unit': 'EUR/MWh'},
            1043: {'name': 'Generación total', 'short_name': 'Total Generation', 'type': 'generation', 'unit': 'MW'},
        }
        
        return {
            'esios_id': indicator_id,
            **defaults.get(indicator_id, {
                'name': f'ESIOS Indicator {indicator_id}',
                'short_name': f'Indicator {indicator_id}',
                'type': 'generation',
                'unit': 'MW'
            })
        }

    def _process_date_range(self, esios_indicator, indicator_obj, indicator_id, 
                           start_date, end_date, chunk_days, resolution):
        """Process the full date range in chunks"""
        current_start = start_date
        total_created = total_updated = 0

        while current_start <= end_date:
            # Calculate chunk end (keep as datetime)
            chunk_end = min(
                current_start + timedelta(days=chunk_days),
                end_date
            )
            
            self.stdout.write(f"📊 Fetching {resolution} chunk: {current_start.date()} to {chunk_end.date()}")

            try:
                # Fetch and process chunk
                chunk_created, chunk_updated = self._process_chunk(
                    esios_indicator, indicator_obj, indicator_id,
                    current_start, chunk_end, resolution
                )
                
                total_created += chunk_created
                total_updated += chunk_updated
                
                if chunk_created > 0 or chunk_updated > 0:
                    self.stdout.write(f"  ✅ {chunk_created} created, {chunk_updated} updated")
                else:
                    self.stdout.write(f"  ⏭️  No new data")

                # Be nice to the API
                time.sleep(0.5)
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Chunk failed: {e}"))
                # Continue with next chunk
                
            # Move to next chunk
            current_start = chunk_end + timedelta(days=1)

        return total_created, total_updated

    def _process_chunk(self, esios_indicator, indicator_obj, indicator_id, 
                      start, end, resolution):
        """Process a single date chunk"""
        
        # Set up API parameters based on resolution
        api_params = {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'geo_ids': [8741],  # Spain electric system
            'geo_trunc': 'electric_system',
        }
        
        if resolution == 'hour':
            api_params.update({
                'time_trunc': 'hour',
                'time_agg': 'average'
            })
        
        # Fetch data from ESIOS
        data = esios_indicator.historical(**api_params)

        # Save data points
        return self._save_data_points(data, indicator_obj, indicator_id, resolution)

    def _save_data_points(self, data, indicator_obj, indicator_id, resolution):
        """Save data points to database"""
        created_count = updated_count = 0
        
        for timestamp, row in data.iterrows():
            value = row[str(indicator_id)]
            geo_id = row.get('geo_id', 8741)
            geo_name = row.get('geo_name', 'Spain')

            # Save to database with resolution
            obj, created = EnergyData.objects.get_or_create(
                indicator=indicator_obj,
                timestamp=timestamp,
                geo_id=geo_id,
                resolution=resolution,
                defaults={
                    'value': value,
                    'geo_name': geo_name,
                }
            )
            
            if created:
                created_count += 1
            elif obj.value != value:
                # Update value if it changed
                obj.value = value
                obj.save(update_fields=['value'])
                updated_count += 1
                
        return created_count, updated_count