# models.py
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