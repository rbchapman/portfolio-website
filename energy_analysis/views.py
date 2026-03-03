# views.py
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from .models import EnergyData, DailyEnergySummary
from .serializers import EnergyDataSerializer
from rest_framework.decorators import action
from .services.daily_summary_service import DailySummaryService
from .utils.data_quality import EnergyDataValidator
import logging
from rest_framework.decorators import action
from rest_framework.response import Response
from .services.bess_decision_service import BESSDecisionService
from .models import BESSConfig
from .services.daily_curtailment_service import DailyCurtailmentService, MonthlyCurtailmentService
from .models import DailyCurtailmentSummary, MonthlyCurtailmentSummary

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
        """Get chart data for any date and region."""
        from .services.region_service import RegionService
        
        date = request.query_params.get('date', '2024-06-20')
        region = request.query_params.get('region', 'california')
        
        try:
            data = RegionService.get_chart_data(region, date)
            return Response({
                'region': region,
                **data
            })
        except ValueError as e:
            logger.error(f"Chart data validation error for {date}: {e}")
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Chart data error for {date} ({region}): {e}")
            return Response({'error': 'Failed to fetch energy data'}, status=500)

        def _get_vre_pct_at_hour(self, hourly_data, target_time):
            """Helper to get VRE percentage at specific hour"""
            target_hour_str = target_time.strftime('%H:%M')
            for hour_data in hourly_data:
                if hour_data['hour'] == target_hour_str:
                    return hour_data['vre_pct']
            return 0

    @action(detail=False, methods=['get'])
    def bess_analysis(self, request):
        date           = request.query_params.get('date', '2024-05-11')
        power_mw       = int(request.query_params.get('power_mw', 100))
        duration_hours = int(request.query_params.get('duration_hours', 4))
        efficiency     = float(request.query_params.get('efficiency', 0.87))

        logger.info("BESS request  date=%s  power=%s MW  duration=%s h  efficiency=%s",
                    date, power_mw, duration_hours, efficiency)

        # 1.  show what the DB really contains
        summary = DailyEnergySummary.objects.get(date=date)
        sample  = summary.hourly_data_json["hourly_data"][0]
        logger.info("DB raw sample (00:00): %s", sample)   # demand, solar, wind, price, ...

        # 2.  run the analysis
        config  = BESSConfig(power_mw=power_mw, duration_hours=duration_hours, efficiency=efficiency)
        analysis = BESSDecisionService.analyze_day(date, config)

        for i, decision in enumerate(analysis['hourly_decisions'][:5]):
            print(f"Hour {decision['hour']}: {decision['action']} - {decision['energy_mwh']} MWh")
            
        # 3.  first hour numbers
        h0 = analysis["hourly_decisions"][0]
        logger.info("Result 00:00  action=%s  energy_mwh=%s  cost_eur=%s  price=%s",
                    h0["action"], h0["energy_mwh"], h0["cost_eur"], h0["price"])

        # 4.  daily totals
        perf = analysis["daily_performance"]
        logger.info("Daily totals  charged=%s MWh  discharged=%s MWh  gross_profit=%s €",
                    perf["energy_charged_mwh"], perf["energy_discharged_mwh"], perf["gross_profit_eur"])

        return Response(analysis)
    
    @action(detail=False, methods=['get'])
    def curtailment_data(self, request):
        """Get curtailment data for any date and region."""
        from .services.region_service import RegionService
        
        date = request.query_params.get('date', '2024-06-20')
        region = request.query_params.get('region', 'california')
        
        try:
            data = RegionService.get_curtailment_data(region, date)
            return Response({
                'region': region,
                **data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Curtailment error for {date} ({region}): {e}")
            return Response({'error': 'Failed to fetch curtailment data'}, status=500)

    @action(detail=False, methods=['get'])
    def curtailment_monthly(self, request):
        """
        Monthly curtailment aggregates for both years - feeds the annual bar chart.
        Returns all available months sorted chronologically.
        """
        try:
            months = MonthlyCurtailmentSummary.objects.all().order_by('year', 'month')

            data = [{
                'year':                       m.year,
                'month':                      m.month,
                'label':                      f"{m.year}-{m.month:02d}",
                'total_curtailed_mwh':        m.total_curtailed_mwh,
                'total_revenue_lost_eur':     m.total_revenue_lost_eur,
                'avg_daily_curtailed_mwh':    m.avg_daily_curtailed_mwh,
                'days_with_curtailment':      m.days_with_curtailment,
                'worst_day':                  m.worst_day.isoformat(),
                'worst_day_mwh':              m.worst_day_mwh,
                'total_curtailment_pct':      m.total_curtailment_pct,
                'transmission_curtailment_pct': m.transmission_curtailment_pct,
                'distribution_curtailment_pct': m.distribution_curtailment_pct,
            } for m in months]

            # Annual totals for the headline stat cards
            annual = {}
            for m in months:
                y = m.year
                if y not in annual:
                    annual[y] = {'total_curtailed_mwh': 0, 'total_revenue_lost_eur': 0}
                annual[y]['total_curtailed_mwh']    += m.total_curtailed_mwh
                annual[y]['total_revenue_lost_eur'] += m.total_revenue_lost_eur

            return Response({
                'monthly_data': data,
                'annual_totals': annual,
            })

        except Exception as e:
            logger.error(f"Monthly curtailment error: {e}")
            return Response({'error': 'Failed to fetch monthly curtailment data'}, status=500)