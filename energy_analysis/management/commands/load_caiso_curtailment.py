# management/commands/load_caiso_curtailment.py
from django.core.management.base import BaseCommand
from energy_analysis.services.gridstatus_service import GridStatusService
from energy_analysis.models import DailyCurtailmentSummary
from datetime import datetime, timedelta
import time
import signal
import sys

class Command(BaseCommand):
    help = 'Load CAISO curtailment data into database'

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
        
        self.stdout.write(f"Starting CAISO curtailment load: {current} to {end}")
        self.stdout.write(f"Start time: {datetime.now()}")
        self.stdout.write("-" * 50)
        
        while current <= end:
            self.last_date = current
            date_str = current.strftime('%Y-%m-%d')
            
            # Skip if exists
            if DailyCurtailmentSummary.objects.filter(date=current, data_source='caiso').exists():
                self.stdout.write(f"Skipping {date_str} - already exists")
                self.skipped += 1
                current += timedelta(days=1)
                continue
            
            self.stdout.write(f"Loading curtailment {date_str}...")
            
            try:
                data = svc.fetch_curtailment_data(date_str)
                if data:
                    insights = data['daily_insights']
                    DailyCurtailmentSummary.objects.create(
                        date=current,
                        data_source='caiso',
                        hourly_data_json={
                            'hourly_data': data['hourly_data'],
                            'curtailment_breakdown': data.get('curtailment_breakdown', {})
                        },
                        total_curtailed_mwh=insights['total_curtailed_mwh'],
                        estimated_revenue_lost_eur=insights['estimated_revenue_lost_usd'],  # Store USD in EUR field
                        peak_curtailment_mwh=insights['peak_curtailment_mwh'],
                        peak_curtailment_hour=datetime.strptime(insights['peak_curtailment_hour'], '%H:%M').time(),
                    )
                    self.created += 1
                    self.stdout.write(self.style.SUCCESS(f"  Saved {date_str} - {insights['total_curtailed_mwh']:.0f} MWh curtailed"))
                else:
                    self.errors += 1
                    self.stdout.write(self.style.WARNING(f"  No data for {date_str}"))
            except Exception as e:
                self.errors += 1
                self.stdout.write(self.style.ERROR(f"  Failed {date_str}: {e}"))
            
            time.sleep(2)  # PDF parsing is slower, be nice
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
            self.stdout.write(f"  python manage.py load_caiso_curtailment {next_date} <end_date>")