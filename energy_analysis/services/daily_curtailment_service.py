from datetime import datetime, date
from django.db.models import Sum
import logging
from ..models import DailyCurtailmentSummary, MonthlyCurtailmentSummary, EnergyData

logger = logging.getLogger(__name__)


class DailyCurtailmentService:

    CURTAIL_DOWN = 721  # redispatch down = actual curtailment (MWh)
    REDISPATCH_UP = 720  # redispatch up = grid called for MORE generation, not curtailment
    SPOT_PRICE   = 600  # EUR/MWh

    @classmethod
    def get_or_create_summary(cls, date_str):
        """
        Main entry point - mirrors DailySummaryService pattern.
        Returns (DailyCurtailmentSummary, created: bool)
        """
        try:
            date_obj = datetime.fromisoformat(date_str).date()
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")

        try:
            summary = DailyCurtailmentSummary.objects.get(date=date_obj)
            return summary, False
        except DailyCurtailmentSummary.DoesNotExist:
            summary = cls._create_summary(date_obj)
            return summary, True

    @classmethod
    def _create_summary(cls, date_obj):
        hourly_data = cls._build_hourly_data(date_obj)
        metrics     = cls._calculate_metrics(hourly_data)

        summary = DailyCurtailmentSummary.objects.create(
            date=date_obj,
            data_source='database',
            hourly_data_json={'hourly_data': hourly_data},
            **metrics
        )
        logger.info(f"Created curtailment summary for {date_obj}: "
                    f"{metrics['total_curtailed_mwh']:.1f} MWh, "
                    f"€{metrics['estimated_revenue_lost_eur']:.0f} lost")
        return summary

    @classmethod
    def _build_hourly_data(cls, date_obj):
        """
        Build a full 24-hour array merging 720, 721, and spot price.
        Missing hours in EnergyData = zero curtailment that hour.
        """
        # Pull all three indicators for the day in one query
        raw = EnergyData.objects.filter(
            timestamp__date=date_obj,
            indicator__indicator_id__in=[cls.CURTAIL_DOWN, cls.REDISPATCH_UP, cls.SPOT_PRICE]
        ).select_related('indicator')

        # Bucket into dicts keyed by hour integer (0-23)
        redispatch_up = {}  # 720 - stored for future congestion analysis
        down          = {}  # 721 - actual curtailment
        price         = {}  # 600

        for row in raw:
            h   = row.timestamp.hour
            ind = row.indicator.indicator_id
            if ind == cls.REDISPATCH_UP:
                redispatch_up[h] = row.value
            elif ind == cls.CURTAIL_DOWN:
                down[h] = row.value
            elif ind == cls.SPOT_PRICE:
                price[h] = row.value

        hourly_data = []
        for h in range(24):
            curtailed_mwh  = down.get(h, 0)
            spot           = price.get(h, 0)
            revenue_lost   = curtailed_mwh * spot if spot > 0 else 0

            hourly_data.append({
                'hour':           f'{h:02d}:00',
                'curtailed_mwh':  round(curtailed_mwh, 1),      # 721 only
                'redispatch_up':  round(redispatch_up.get(h, 0), 1),  # 720 - congestion signal
                'spot_price':     round(spot, 2),
                'revenue_lost':   round(revenue_lost, 2),
            })

        return hourly_data

    @classmethod
    def _calculate_metrics(cls, hourly_data):
        """Derive summary fields from hourly array."""
        total_curtailed = sum(h['curtailed_mwh'] for h in hourly_data)
        total_revenue   = sum(h['revenue_lost']   for h in hourly_data)

        # Peak curtailment hour
        peak_hour = max(hourly_data, key=lambda h: h['curtailed_mwh'])

        return {
            'total_curtailed_mwh':        round(total_curtailed, 1),
            'estimated_revenue_lost_eur': round(total_revenue, 2),
            'peak_curtailment_mwh':       round(peak_hour['curtailed_mwh'], 1),
            'peak_curtailment_hour':      datetime.strptime(peak_hour['hour'], '%H:%M').time(),
        }


class MonthlyCurtailmentService:

    @classmethod
    def build_month(cls, year, month):
        """
        Aggregate daily summaries into a MonthlyCurtailmentSummary.
        Call this after all daily summaries for the month are created.
        """
        dailies = DailyCurtailmentSummary.objects.filter(
            date__year=year,
            date__month=month
        )

        if not dailies.exists():
            logger.warning(f"No daily curtailment data for {year}-{month:02d}")
            return None

        total_mwh     = sum(d.total_curtailed_mwh        for d in dailies)
        total_revenue = sum(d.estimated_revenue_lost_eur for d in dailies)
        days_with     = dailies.filter(total_curtailed_mwh__gt=0).count()
        worst         = max(dailies, key=lambda d: d.total_curtailed_mwh)

        # Pull monthly percentage indicators from EnergyData
        pct_10462 = cls._get_monthly_pct(year, month, 10462)
        pct_10458 = cls._get_monthly_pct(year, month, 10458)
        pct_10459 = cls._get_monthly_pct(year, month, 10459)

        summary, _ = MonthlyCurtailmentSummary.objects.update_or_create(
            year=year,
            month=month,
            defaults={
                'total_curtailed_mwh':        round(total_mwh, 1),
                'total_revenue_lost_eur':      round(total_revenue, 2),
                'avg_daily_curtailed_mwh':     round(total_mwh / dailies.count(), 1),
                'days_with_curtailment':       days_with,
                'worst_day':                   worst.date,
                'worst_day_mwh':               worst.total_curtailed_mwh,
                'total_curtailment_pct':       pct_10462,
                'transmission_curtailment_pct': pct_10458,
                'distribution_curtailment_pct': pct_10459,
            }
        )
        return summary

    @classmethod
    def _get_monthly_pct(cls, year, month, indicator_id):
        """Fetch the single monthly percentage value for a given indicator."""
        row = EnergyData.objects.filter(
            indicator__indicator_id=indicator_id,
            timestamp__year=year,
            timestamp__month=month
        ).first()
        return round(row.value, 4) if row else None

    @classmethod
    def build_all(cls, years=(2024, 2025)):
        """Convenience method to roll up all months for given years."""
        for year in years:
            for month in range(1, 13):
                result = cls.build_month(year, month)
                if result:
                    logger.info(f"Built monthly summary {year}-{month:02d}: "
                                f"{result.total_curtailed_mwh:.1f} MWh")