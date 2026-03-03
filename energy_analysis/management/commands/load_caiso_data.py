# management/commands/load_caiso_data.py
from django.core.management.base import BaseCommand
from energy_analysis.services.gridstatus_service import GridStatusService
from energy_analysis.models import DailyEnergySummary
from datetime import datetime, timedelta
import time

class Command(BaseCommand):
    help = 'Load CAISO data into database'

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=str, help='YYYY-MM-DD')
        parser.add_argument('end_date', type=str, help='YYYY-MM-DD')

    def handle(self, *args, **options):
        svc = GridStatusService('caiso')
        current = datetime.fromisoformat(options['start_date']).date()
        end = datetime.fromisoformat(options['end_date']).date()
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            
            # Skip if exists
            if DailyEnergySummary.objects.filter(date=current, data_source='caiso').exists():
                self.stdout.write(f"Skipping {date_str} - already exists")
                current += timedelta(days=1)
                continue
            
            self.stdout.write(f"Loading {date_str}...")
            
            try:
                data = svc.fetch_day_data(date_str)
                if data:
                    DailyEnergySummary.objects.create(
                        date=current,
                        data_source='caiso',
                        hourly_data_json={
                            'hourly_data': data['hourly_data'],
                            'daily_insights': data['daily_insights']
                        },
                        # Fill required fields with defaults/calculated values
                        peak_vre_penetration=data['daily_insights']['peak_vre_pct'],
                        peak_vre_hour=datetime.strptime(data['daily_insights']['peak_vre_hour'], '%H:%M').time(),
                        peak_demand_hour=datetime.strptime(data['daily_insights']['shift_from_hour'], '%H:%M').time(),
                        sustained_high_vre_hours=data['daily_insights']['high_vre_window_hours'],
                        max_netload_ramp_gw=data['daily_insights']['max_ramp_gw'],
                        ramp_window_start=datetime.strptime(data['daily_insights']['ramp_window'].split('-')[0], '%H:%M').time(),
                        ramp_window_end=datetime.strptime(data['daily_insights']['ramp_window'].split('-')[1], '%H:%M').time(),
                        load_balancing_gap_hours=data['daily_insights']['load_balancing_gap_hours'],
                        shiftable_energy_gwh=data['daily_insights']['optimal_shift_amount'],
                        flexibility_window_start=datetime.strptime(data['daily_insights']['flexibility_window_start'], '%H:%M').time() if data['daily_insights']['flexibility_window_start'] else None,
                        flexibility_window_end=datetime.strptime(data['daily_insights']['flexibility_window_end'], '%H:%M').time() if data['daily_insights']['flexibility_window_end'] else None,
                    )
                    self.stdout.write(self.style.SUCCESS(f"  Saved {date_str}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  No data for {date_str}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Failed {date_str}: {e}"))
            
            time.sleep(1)  # Be nice to CAISO
            current += timedelta(days=1)