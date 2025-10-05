import esios
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class EsiosService:
    """Service for fetching real-time data from ESIOS API"""
    
    INDICATORS = {
        'demand': 1293,
        'solar': 1161, 
        'wind': 1159
    }
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the ESIOS client"""
        try:
            self.client = esios.ESIOSClient()
            logger.info("ESIOS client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ESIOS client: {e}")
            self.client = None
    
    def fetch_day_data(self, date_string: str) -> Optional[Dict]:
        """
        Fetch a single day's data from ESIOS
        
        Args:
            date_string: Date in format 'YYYY-MM-DD'
            
        Returns:
            Dict with hourly data points or None if failed
        """
        if not self.client:
            logger.error("ESIOS client not initialized")
            return None
            
        try:
            # Convert date string to datetime range (full day)
            target_date = datetime.fromisoformat(date_string)
            start_dt = target_date.replace(hour=0, minute=0, second=0)
            end_dt = target_date.replace(hour=23, minute=59, second=59)
            
            logger.info(f"Fetching ESIOS data for {date_string}")
            
            # Fetch all indicators for this day
            raw_data = self._fetch_indicators(start_dt, end_dt)
            
            if raw_data is None or raw_data.empty:
                logger.warning(f"No data returned for {date_string}")
                return None
                
            # Transform to expected format
            return self._transform_to_hourly_data(raw_data, date_string)
            
        except Exception as e:
            logger.error(f"Failed to fetch day data for {date_string}: {e}")
            return None
    
    def _fetch_indicators(self, start_dt: datetime, end_dt: datetime) -> Optional[pd.DataFrame]:
        """Fetch all indicators and combine into single DataFrame"""
        combined_data = pd.DataFrame()
        
        for indicator_name, indicator_id in self.INDICATORS.items():
            try:
                logger.debug(f"Fetching indicator {indicator_id} ({indicator_name})")
                
                # Get the indicator endpoint
                esios_indicator = self.client.endpoint('indicators').select(indicator_id)
                
                # Base API params
                api_params = {
                    'start': start_dt.isoformat(),
                    'end': end_dt.isoformat(),
                    'geo_trunc': 'electric_system',
                    'geo_agg': 'sum'
                }
                
                # Only demand needs time aggregation (5min -> hourly)
                if indicator_name == 'demand':
                    api_params.update({
                        'time_trunc': 'hour',
                        'time_agg': 'average'
                    })
                
                data = esios_indicator.historical(**api_params)
                
                if data.empty:
                    logger.warning(f"Empty data for indicator {indicator_id}")
                    continue
                
                # Only keep the data column we need, rename it
                data_column = data[[str(indicator_id)]].rename(columns={str(indicator_id): indicator_name})
                
                # Combine with other indicators
                if combined_data.empty:
                    combined_data = data_column
                else:
                    combined_data = combined_data.join(data_column, how='outer')
                    
            except Exception as e:
                logger.error(f"Failed to fetch indicator {indicator_id}: {e}")
                continue
        
        return combined_data if not combined_data.empty else None
    
    def _transform_to_hourly_data(self, df: pd.DataFrame, date_string: str) -> Dict:
        """Transform pandas DataFrame to expected format"""
        hourly_data = []
        
        # Iterate through hours and build the expected structure
        for timestamp, row in df.iterrows():
            hour_str = timestamp.strftime('%H:00')
            
            # Get values, defaulting to 0 if missing
            demand = float(row.get('demand', 0)) / 1000
            solar = float(row.get('solar', 0)) / 1000
            wind = float(row.get('wind', 0)) / 1000
            vre_total = solar + wind
            
            # Calculate percentages (avoid division by zero)
            solar_pct = round((solar / demand * 100) if demand > 0 else 0, 1)
            wind_pct = round((wind / demand * 100) if demand > 0 else 0, 1)
            vre_pct = round((vre_total / demand * 100) if demand > 0 else 0, 1)
            
            hourly_data.append({
                'hour': hour_str,
                'demand': round(demand, 1),
                'solar': round(solar, 1),
                'wind': round(wind, 1),
                'vre_total': round(vre_total, 1),
                'solar_pct': solar_pct,
                'wind_pct': wind_pct,
                'vre_pct': vre_pct
            })
        
        return {
            'date': date_string,
            'hourly_data': hourly_data
        }