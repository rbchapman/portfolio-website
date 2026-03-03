from django.db import models
from dataclasses import dataclass
from typing import Literal
class EnergyIndicator(models.Model):
    """indicator metadata"""
    indicator_id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=20)

    class Meta:
        ordering = ['indicator_id']
    
    def __str__(self):
        return f"{self.indicator_id}: {self.name}"
class EnergyData(models.Model):
    """Time series energy data points"""
    indicator = models.ForeignKey(EnergyIndicator, on_delete=models.CASCADE, related_name='data_points')
    timestamp = models.DateTimeField(db_index=True)
    value = models.FloatField()
    resolution = models.CharField(max_length=20, choices=[
        ('fifteen_minutes', '15 minutes'),
        ('hour', 'hourly'),
        ('day', 'daily'),
        ('month', 'monthly'),
        ('year', 'yearly'),
    ], default='hour')
    
    class Meta:
        unique_together = ['indicator', 'timestamp', 'resolution']
        indexes = [
            models.Index(fields=['indicator', 'timestamp']),
        ]
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.indicator.name}: {self.value} {self.indicator.unit} at {self.timestamp}"
    
class DailyEnergySummary(models.Model):
    # Core identification
    date = models.DateField(db_index=True)
    data_source = models.CharField(max_length=20, choices=[
        ('database', 'Local Database'),
        ('esios', 'ESIOS API'),
        ('caiso', 'CAISO'),
        {'spp', 'SPP'}
    ])
    
    # Visibility - Real-time grid awareness
    peak_vre_penetration = models.FloatField()  # % of demand
    peak_vre_hour = models.TimeField()  # When it happened
    sustained_high_vre_hours = models.IntegerField()  # Hours >70%
    
    # Analytics & Forecasting - System stress prediction
    max_netload_ramp_gw = models.FloatField()  # Biggest 2-hour swing
    ramp_window_start = models.TimeField()  # When ramp began
    ramp_window_end = models.TimeField()    # When ramp ended
    
    # Flexibility Management - Demand response opportunity
    load_balancing_gap_hours = models.IntegerField()  # Time between peaks
    peak_demand_hour = models.TimeField()
    shiftable_energy_gwh = models.FloatField()  # Available for shifting
    flexibility_window_start = models.TimeField(null=True)  # High VRE period start
    flexibility_window_end = models.TimeField(null=True)    # High VRE period end
    
    # Chart data storage
    hourly_data_json = models.JSONField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    total_hours = models.IntegerField(default=24)
    
    def set_total_hours(self):
        """Calculate and store total hours of data available"""
        if not self.hourly_data_json or not self.hourly_data_json.get('hourly_data'):
            self.total_hours = 0
        else:
            self.total_hours = len(self.hourly_data_json['hourly_data'])
        
        self.save(update_fields=['total_hours'])
    class Meta:
        unique_together = ['date', 'data_source']
        ordering = ['-date']
        verbose_name = "Daily Energy Summary"
        verbose_name_plural = "Daily Energy Summaries"

class DailyCurtailmentSummary(models.Model):
    date = models.DateField(db_index=True)
    data_source = models.CharField(max_length=20, choices=[
        ('database', 'Local Database'),
        ('esios', 'ESIOS API'),
        ('caiso', 'CAISO'),
        ('spp', 'SPP')
    ])

    # Daily totals from 721 (MWh)
    total_curtailed_mwh = models.FloatField()
    estimated_revenue_lost_eur = models.FloatField()

    # Peak curtailment moment
    peak_curtailment_mwh = models.FloatField()   # highest single hour (720+721)
    peak_curtailment_hour = models.TimeField()

    # Constraint type breakdown - monthly only (10458/10459), null until loaded
    # TODO: future enhancement - forecast vs actual delta using 701/702
    transmission_curtailment_pct = models.FloatField(null=True, blank=True)   # 10458
    distribution_curtailment_pct = models.FloatField(null=True, blank=True)   # 10459

    # Raw hourly breakdown for day-view chart
    # sparse data - hours with no curtailment will have value 0
    hourly_data_json = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['date', 'data_source']
        ordering = ['-date']
        verbose_name = "Daily Curtailment Summary"
        verbose_name_plural = "Daily Curtailment Summaries"

    def __str__(self):
        return f"{self.date}: {self.total_curtailed_mwh:.1f} MWh, €{self.estimated_revenue_lost_eur:.0f} lost"
class MonthlyCurtailmentSummary(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()  # 1-12

    # Volume rollup from DailyCurtailmentSummary
    total_curtailed_mwh = models.FloatField()
    total_revenue_lost_eur = models.FloatField()
    avg_daily_curtailed_mwh = models.FloatField()
    days_with_curtailment = models.IntegerField()

    # Worst day of the month
    worst_day = models.DateField()
    worst_day_mwh = models.FloatField()

    # Monthly percentage indicators loaded directly from ESIOS
    total_curtailment_pct = models.FloatField(null=True, blank=True)        # 10462
    transmission_curtailment_pct = models.FloatField(null=True, blank=True) # 10458
    distribution_curtailment_pct = models.FloatField(null=True, blank=True) # 10459

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['year', 'month']
        ordering = ['year', 'month']
        verbose_name = "Monthly Curtailment Summary"
        verbose_name_plural = "Monthly Curtailment Summaries"

    def __str__(self):
        return f"{self.year}-{self.month:02d}: {self.total_curtailed_mwh:.1f} MWh, €{self.total_revenue_lost_eur:.0f}"
@dataclass
class BESSConfig:
    """
    Battery Energy Storage System configuration.
    
    Note on C-Rate: Not stored directly as it's derived (power_mw / capacity_mwh).
    C-Rate determines how quickly the battery charges/discharges:
    - 1C = full charge/discharge in 1 hour (100MW/100MWh)
    - 0.5C = full charge/discharge in 2 hours (100MW/200MWh)
    - 0.25C = full charge/discharge in 4 hours (100MW/400MWh)
    
    Higher C-Rate = more power cycling capability = better arbitrage potential
    but typically shorter battery life and higher costs.
    """
    
    # User-configurable parameters (the only 3 things users adjust)
    power_mw: int  # Charge/discharge rate (50-200 MW typical range)
    duration_hours: Literal[2, 4, 6]  # Storage duration options
    efficiency: float  # Round-trip efficiency (0.85-0.92 for lithium-ion)
    
    # Fixed operational constraints for MVP
    min_soc: int = 10  # Minimum state of charge % (battery protection)
    max_soc: int = 90  # Maximum state of charge % (battery protection)
    
    @property
    def capacity_mwh(self) -> float:
        """Total energy capacity in MWh"""
        return self.power_mw * self.duration_hours
    
    @property
    def c_rate(self) -> float:
        """
        C-Rate: Power capability relative to capacity.
        
        Example: 100MW / 400MWh = 0.25C
        This means the battery can charge from empty to full in 4 hours.
        
        Industry context:
        - Utility BESS typically 0.25C-0.5C (2-4 hour duration)
        - Frequency regulation BESS often 1C+ (sub-hourly response)
        - Higher C-Rate = better for price arbitrage but more degradation
        """
        return self.power_mw / self.capacity_mwh if self.capacity_mwh > 0 else 0
    
    def __post_init__(self):
        """Validate configuration on instantiation"""
        if not 50 <= self.power_mw <= 200:
            raise ValueError("Power must be between 50-200 MW")
        if self.duration_hours not in [2, 4, 6]:
            raise ValueError("Duration must be 2, 4, or 6 hours")
        if not 0.85 <= self.efficiency <= 0.92:
            raise ValueError("Efficiency must be between 0.85-0.92")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'power_mw': self.power_mw,
            'duration_hours': self.duration_hours,
            'capacity_mwh': self.capacity_mwh,
            'efficiency': self.efficiency,
            'c_rate': round(self.c_rate, 2),
            'min_soc': self.min_soc,
            'max_soc': self.max_soc
        }