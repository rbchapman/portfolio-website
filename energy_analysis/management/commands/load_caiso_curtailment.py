# management/commands/load_caiso_curtailment.py
from django.core.management.base import BaseCommand
from energy_analysis.services.gridstatus_service import GridStatusService
from energy_analysis.models import DailyCurtailmentSummary
from datetime import datetime, timedelta
import time

class Command(BaseCommand):
    help = 'Load CAISO curtailment data into database'

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
            if DailyCurtailmentSummary.objects.filter(date=current, data_source='caiso').exists():
                self.stdout.write(f"Skipping {date_str} - already exists")
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
                        estimated_revenue_lost_eur=insights['estimated_revenue_lost_usd'],  # Store USD in EUR field for now
                        peak_curtailment_mwh=insights['peak_curtailment_mwh'],
                        peak_curtailment_hour=datetime.strptime(insights['peak_curtailment_hour'], '%H:%M').time(),
                    )
                    self.stdout.write(self.style.SUCCESS(f"  Saved {date_str} - {insights['total_curtailed_mwh']} MWh curtailed"))
                else:
                    self.stdout.write(self.style.WARNING(f"  No data for {date_str}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Failed {date_str}: {e}"))
            
            time.sleep(2)  # PDF parsing is slow, be nice
            current += timedelta(days=1)