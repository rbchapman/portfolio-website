from django.db import models


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
    date = models.DateField(unique=True, db_index=True)
    data_source = models.CharField(max_length=20, choices=[
        ('database', 'Local Database'),
        ('esios', 'ESIOS API')
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
        ordering = ['-date']
        verbose_name = "Daily Energy Summary"
        verbose_name_plural = "Daily Energy Summaries"