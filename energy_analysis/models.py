# models.py
from django.db import models
from decimal import Decimal


class EnergyIndicator(models.Model):
    """ESIOS indicator metadata"""
    esios_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=500)
    short_name = models.CharField(max_length=200, blank=True)
    unit = models.CharField(max_length=50, default='MWh')
    
    # Clear separation of data type vs technology
    type = models.CharField(max_length=20, choices=[
        ('generation', 'Generation'),
        ('demand', 'Demand'),
        ('price', 'Price'),
        ('percentage', 'Percentage'),
    ])
    
    technology = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('solar_pv', 'Solar Photovoltaic'),
        ('solar_thermal', 'Solar Thermal'),
        ('wind_onshore', 'Wind Onshore'),
        ('wind_offshore', 'Wind Offshore'),
        ('hydro_large', 'Hydro Large'),
        ('hydro_small', 'Hydro Small'),
        ('nuclear', 'Nuclear'),
        ('biomass', 'Biomass'),
        ('biogas', 'Biogas'),
        ('renewable_waste', 'Renewable Waste'),
    ])
    
    is_renewable = models.BooleanField(default=False)
    is_variable_renewable = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['esios_id']
    
    def __str__(self):
        return f"{self.esios_id}: {self.short_name or self.name}"

class EnergyData(models.Model):
   """Time series energy data points"""
   indicator = models.ForeignKey(EnergyIndicator, on_delete=models.CASCADE, related_name='data_points')
   timestamp = models.DateTimeField(db_index=True)
   value = models.FloatField()
   resolution = models.CharField(max_length=10, choices=[
        ('5min', '5 minute'),
        ('hour', 'Hourly'),
    ], default='hour')
   geo_id = models.IntegerField(null=True, blank=True)
   geo_name = models.CharField(max_length=100, blank=True)
   data_source = models.CharField(max_length=50, default='esios')
   created_at = models.DateTimeField(auto_now_add=True)
   
   class Meta:
       unique_together = ['indicator', 'timestamp', 'geo_id', 'resolution']
       indexes = [
           models.Index(fields=['timestamp', 'indicator']),
           models.Index(fields=['indicator', 'timestamp']),
           models.Index(fields=['geo_id']),
       ]
       ordering = ['timestamp']
   
   def __str__(self):
       geo_part = f" ({self.geo_name})" if self.geo_name else ""
       return f"{self.indicator.short_name}: {self.value}{geo_part} at {self.timestamp}"

class DailyEnergySummary(models.Model):
    """Minimal daily summaries focused on BESS analysis"""
    date = models.DateField(unique=True, db_index=True)
    
    # Core BESS analysis data
    renewable_generation_mwh = models.FloatField()
    total_demand_mwh = models.FloatField()
    renewable_surplus_mwh = models.FloatField()
    
    # Percentage for easy interpretation
    renewable_percentage = models.FloatField()
    
    # Price data for profitability analysis
    avg_price_eur_mwh = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date}: {self.renewable_surplus_mwh:.0f} MWh surplus"
    
    @property
    def has_surplus(self):
        """Simple boolean check"""
        return self.renewable_surplus_mwh > 0
    
    @property
    def surplus_category(self):
        """Human-readable surplus level"""
        if self.renewable_surplus_mwh > 5000:
            return "High"
        elif self.renewable_surplus_mwh > 1000:
            return "Medium" 
        elif self.renewable_surplus_mwh > 0:
            return "Low"
        else:
            return "None"
    
    @property
    def is_profitable_surplus(self):
        """Quick check if surplus occurred during low prices (good for storage)"""
        if not self.has_surplus or not self.avg_price_eur_mwh:
            return False
        return self.avg_price_eur_mwh < 30  # Arbitrary threshold - tune based on data


# Utility function to create initial indicators
def create_initial_indicators():
    """Create the basic indicators we need for initial analysis"""
    indicators = [
        # Core renewable generation
        {'esios_id': 1161, 'name': 'Generación medida Solar fotovoltaica', 'short_name': 'Solar PV', 
         'type': 'generation', 'technology': 'solar_pv', 'is_renewable': True, 'is_variable_renewable': True},
        {'esios_id': 1159, 'name': 'Generación medida Eólica terrestre', 'short_name': 'Wind Onshore',
         'type': 'generation', 'technology': 'wind_onshore', 'is_renewable': True, 'is_variable_renewable': True},
        {'esios_id': 1150, 'name': 'Generación medida Hidráulica UGH', 'short_name': 'Hydro Large',
         'type': 'generation', 'technology': 'hydro_large', 'is_renewable': True, 'is_variable_renewable': False},
        {'esios_id': 1151, 'name': 'Generación medida Hidráulica no UGH', 'short_name': 'Hydro Small',
         'type': 'generation', 'technology': 'hydro_small', 'is_renewable': True, 'is_variable_renewable': False},
        
        # Nuclear (for validation)
        {'esios_id': 1153, 'name': 'Generación medida Nuclear', 'short_name': 'Nuclear',
         'type': 'generation', 'technology': 'nuclear', 'is_renewable': False, 'is_variable_renewable': False},
        
        # System totals and validation
        {'esios_id': 1043, 'name': 'Generación medida total', 'short_name': 'Total Generation',
         'type': 'generation', 'technology': None, 'is_renewable': False, 'is_variable_renewable': False},
        {'esios_id': 10033, 'name': 'Porcentaje de generación libre de CO2', 'short_name': 'Clean Energy %',
         'type': 'percentage', 'technology': None, 'is_renewable': False, 'is_variable_renewable': False, 'unit': '%'},
        
        # Demand
        {'esios_id': 1293, 'name': 'Demanda real', 'short_name': 'Demand',
         'type': 'demand', 'technology': None, 'is_renewable': False, 'is_variable_renewable': False, 'unit': 'MW'},
        
        # Prices
        {'esios_id': 600, 'name': 'Precio mercado SPOT Diario', 'short_name': 'Spot Price',
         'type': 'price', 'technology': None, 'is_renewable': False, 'is_variable_renewable': False, 'unit': 'EUR/MWh'},
    ]
    
    created_indicators = []
    for indicator_data in indicators:
        indicator, created = EnergyIndicator.objects.get_or_create(
            esios_id=indicator_data['esios_id'],
            defaults=indicator_data
        )
        if created:
            created_indicators.append(indicator)
    
    return created_indicators