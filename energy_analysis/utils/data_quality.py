from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class EnergyDataValidator:
    """Utility class for validating energy data quality"""
    
    @staticmethod
    def assess_hourly_data_quality(hourly_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess data completeness and quality for hourly energy data
        
        Args:
            hourly_data: List of hourly data dictionaries
            
        Returns:
            Dict with quality assessment results
        """
        if not hourly_data:
            return {
                'complete': False,
                'total_hours': 0,
                'generation_hours': 0,
                'issues': ['no_data']
            }
        
        total_hours = len(hourly_data)
        generation_hours = sum(
            1 for hour in hourly_data 
            if hour.get('solar', 0) > 0 or hour.get('wind', 0) > 0
        )
        
        issues = []
        
        # Check for incomplete hourly data (should be close to 24 hours)
        if total_hours < 20:
            issues.append("incomplete_hourly")
        
        # Check for missing generation data
        if generation_hours == 0:
            issues.append("no_generation")
        
        # Check for sparse generation data (less than 50% of hours have generation)
        elif generation_hours < total_hours * 0.5:
            issues.append("sparse_generation")
        
        # Check for unrealistic demand values (basic sanity check)
        demand_values = [hour.get('demand', 0) for hour in hourly_data]
        if demand_values:
            max_demand = max(demand_values)
            min_demand = min(demand_values)
            # Spain's demand typically ranges 15-40 GW
            if max_demand > 50 or min_demand < 10:
                issues.append("unusual_demand_range")
        
        logger.debug(f"Data quality assessment: {total_hours} hours, {generation_hours} with generation, issues: {issues}")
        
        return {
            'complete': len(issues) == 0,
            'total_hours': total_hours,
            'generation_hours': generation_hours,
            'issues': issues
        }
    
    @staticmethod
    def get_quality_message(quality_assessment: Dict[str, Any]) -> str:
        """
        Convert quality assessment into user-friendly message
        
        Args:
            quality_assessment: Result from assess_hourly_data_quality
            
        Returns:
            User-friendly error message or empty string if no issues
        """
        if quality_assessment.get('complete', True):
            return ""
        
        issues = quality_assessment.get('issues', [])
        
        if 'no_data' in issues:
            return 'No data available for this date'
        elif 'incomplete_hourly' in issues:
            hours = quality_assessment.get('total_hours', 0)
            return f'Limited hourly data available ({hours} hours) - system reporting gaps detected'
        elif 'no_generation' in issues:
            return 'Generation data processing in progress - demand data available for analysis'
        elif 'sparse_generation' in issues:
            return 'Partial generation data - some reporting intervals missing'
        elif 'unusual_demand_range' in issues:
            return 'Data validation warning - unusual demand values detected'
        
        return 'Data quality issues detected - please verify results'