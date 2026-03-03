from django.core.management.base import BaseCommand
from datetime import date, timedelta
from energy_analysis.services.daily_curtailment_service import DailyCurtailmentService, MonthlyCurtailmentService


class Command(BaseCommand):
    help = 'Backfill DailyCurtailmentSummary and MonthlyCurtailmentSummary'

    def add_arguments(self, parser):
        parser.add_argument('--start', type=str, default='2024-01-01')
        parser.add_argument('--end',   type=str, default='2025-12-31')
        parser.add_argument('--skip-monthly', action='store_true')

    def handle(self, *args, **options):
        start = date.fromisoformat(options['start'])
        end   = date.fromisoformat(options['end'])

        current      = start
        created      = skipped = errors = 0

        while current <= end:
            try:
                _, was_created = DailyCurtailmentService.get_or_create_summary(current.isoformat())
                if was_created:
                    created += 1
                else:
                    skipped += 1

                # Progress every 30 days
                if (created + skipped) % 30 == 0:
                    self.stdout.write(f"  {current} — {created} created, {skipped} skipped, {errors} errors")

            except Exception as e:
                errors += 1
                self.stdout.write(self.style.WARNING(f"  Failed {current}: {e}"))

            current += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(
            f'Daily backfill complete: {created} created, {skipped} skipped, {errors} errors'
        ))

        if not options['skip_monthly']:
            self.stdout.write('Building monthly summaries...')
            MonthlyCurtailmentService.build_all(years=(2024, 2025))
            self.stdout.write(self.style.SUCCESS('Monthly summaries complete'))