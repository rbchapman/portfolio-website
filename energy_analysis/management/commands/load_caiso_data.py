# management/commands/load_caiso_data.py
from django.core.management.base import BaseCommand
from energy_analysis.services.gridstatus_service import GridStatusService
from energy_analysis.models import DailyEnergySummary
from datetime import datetime, timedelta
import time
import signal
import sys

class Command(BaseCommand):
    help = 'Load CAISO data into database'

    def __init__(self):
        super().__init__()
        self.created = 0
        self.skipped = 0
        self.errors = 0
        self.last_date = None

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=str, help='YYYY-MM-DD')
        parser.add_argument('end_date', type=str, help='YYYY-MM-DD')

    def handle(self, *args, **options):
        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, self.handle_interrupt)
        signal.signal(signal.SIGTERM, self.handle_interrupt)
        
        svc = GridStatusService('caiso')
        current = datetime.fromisoformat(options['start_date']).date()
        end = datetime.fromisoformat(options['end_date']).date()
        
        self.stdout.write(f"Starting CAISO load: {current} to {end}")
        self.stdout.write(f"Start time: {datetime.now()}")
        self.stdout.write("-" * 50)
        
        while current <= end:
            self.last_date = current
            date_str = current.strftime('%Y-%m-%d')
            
            # Skip if exists
            if DailyEnergySummary.objects.filter(date=current, data_source='caiso').exists():
                self.stdout.write(f"Skipping {date_str} - already exists")
                self.skipped += 1
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
                    self.created += 1
                    self.stdout.write(self.style.SUCCESS(f"  Saved {date_str}"))
                else:
                    self.errors += 1
                    self.stdout.write(self.style.WARNING(f"  No data for {date_str}"))
            except Exception as e:
                self.errors += 1
                self.stdout.write(self.style.ERROR(f"  Failed {date_str}: {e}"))
            
            time.sleep(1)
            current += timedelta(days=1)
        
        self.print_summary("COMPLETED")

    def handle_interrupt(self, signum, frame):
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.WARNING("INTERRUPTED!"))
        self.print_summary("INTERRUPTED")
        sys.exit(1)

    def print_summary(self, status):
        self.stdout.write("=" * 50)
        self.stdout.write(f"Status: {status}")
        self.stdout.write(f"End time: {datetime.now()}")
        self.stdout.write(f"Last date processed: {self.last_date}")
        self.stdout.write(f"Created: {self.created}")
        self.stdout.write(f"Skipped: {self.skipped}")
        self.stdout.write(f"Errors: {self.errors}")
        self.stdout.write("=" * 50)
        if status == "INTERRUPTED" and self.last_date:
            next_date = self.last_date + timedelta(days=1)
            self.stdout.write(f"To resume, run:")
            self.stdout.write(f"  python manage.py load_caiso_data {next_date} <end_date>")