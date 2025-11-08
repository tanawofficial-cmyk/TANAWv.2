"""
Forecast Accuracy Tracker
Sends forecast data to Node.js backend for accuracy tracking
Part of Objective 3.3: Adaptive Learning & User Feedback - Phase 2
"""

import requests
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta

class ForecastAccuracyTracker:
    def __init__(self):
        self.backend_url = os.getenv('BACKEND_URL', 'http://localhost:5000')
        self.enabled = True
    
    def track_forecast(self, user_id: str, dataset_id: str, forecast_chart: Dict[str, Any]) -> bool:
        """
        Send forecast data to backend for accuracy tracking
        
        Args:
            user_id: MongoDB user ID
            dataset_id: MongoDB dataset ID
            forecast_chart: Chart data containing forecast information
            
        Returns:
            bool: True if tracking successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Extract forecast details from chart
            chart_id = forecast_chart.get('id', 'unknown_forecast')
            chart_title = forecast_chart.get('title', 'Forecast')
            
            # Determine forecast type
            forecast_type = self._determine_forecast_type(chart_id, chart_title)
            domain = self._determine_domain(chart_id, chart_title)
            
            if not forecast_type:
                print(f"ℹ️ Not a trackable forecast type: {chart_id}")
                return False
            
            # Extract forecast data points
            chart_data = forecast_chart.get('data', [])
            forecast_points = self._extract_forecast_points(chart_data, forecast_type)
            
            if not forecast_points:
                print(f"⚠️ No forecast points found in chart: {chart_id}")
                return False
            
            # Get model parameters if available
            model_params = forecast_chart.get('insights', {}).get('modelParameters', forecast_chart.get('modelParameters', {}))
            
            # Create ONE forecast accuracy record (using the last forecast point - 30-day target)
            # This is the most important forecast point for accuracy tracking
            target_point = forecast_points[-1]  # Last point = 30 days out
            
            success = self._create_accuracy_record(
                user_id=user_id,
                dataset_id=dataset_id,
                chart_id=chart_id,
                chart_title=chart_title,
                forecast_type=forecast_type,
                domain=domain,
                forecast_point=target_point,
                model_params=model_params
            )
            
            tracked_count = 1 if success else 0
            
            if tracked_count > 0:
                print(f"✅ Tracked {tracked_count} forecast points for accuracy monitoring")
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error tracking forecast: {e}")
            return False
    
    def _determine_forecast_type(self, chart_id: str, chart_title: str) -> str:
        """Determine forecast type from chart ID/title"""
        chart_id_lower = chart_id.lower()
        title_lower = chart_title.lower()
        
        if 'sales' in chart_id_lower or 'sales forecast' in title_lower:
            return 'sales'
        elif 'quantity' in chart_id_lower or 'demand' in chart_id_lower or 'quantity forecast' in title_lower:
            return 'quantity'
        elif 'stock' in chart_id_lower or 'inventory' in chart_id_lower or 'stock forecast' in title_lower:
            return 'stock'
        elif 'cash' in chart_id_lower or 'cash flow' in title_lower:
            return 'cash_flow'
        
        return None
    
    def _determine_domain(self, chart_id: str, chart_title: str) -> str:
        """Determine business domain from chart ID/title"""
        chart_id_lower = chart_id.lower()
        title_lower = chart_title.lower()
        
        if 'quantity' in chart_id_lower or 'demand' in chart_id_lower:
            return 'product'
        elif 'stock' in chart_id_lower or 'inventory' in chart_id_lower:
            return 'inventory'
        elif 'cash' in chart_id_lower:
            return 'finance'
        else:
            return 'sales'
    
    def _extract_forecast_points(self, chart_data, forecast_type: str) -> List[Dict]:
        """Extract forecast data points from chart data (handles both list and dict formats)"""
        forecast_points = []
        
        # Handle list format: [{x, y, type: 'forecast'}, ...]
        if isinstance(chart_data, list):
            for point in chart_data:
                if isinstance(point, dict):
                    point_type = point.get('type', '')
                    
                    # Only track forecast points (not historical)
                    if point_type == 'forecast':
                        forecast_points.append({
                            'date': point.get('x'),
                            'predicted': point.get('y'),
                            'lower': point.get('lower'),
                            'upper': point.get('upper')
                        })
        
        # Handle dict format: {x: [...], y: [...], forecast_line: N, upper_bound: [...], lower_bound: [...]}
        elif isinstance(chart_data, dict):
            x_values = chart_data.get('x', [])
            y_values = chart_data.get('y', [])
            upper_values = chart_data.get('upper_bound', [])
            lower_values = chart_data.get('lower_bound', [])
            forecast_line = chart_data.get('forecast_line', 0)
            
            # Forecast points start after forecast_line index
            if forecast_line > 0 and len(x_values) > forecast_line:
                for i in range(forecast_line, len(x_values)):
                    forecast_points.append({
                        'date': x_values[i],
                        'predicted': y_values[i] if i < len(y_values) else None,
                        'lower': lower_values[i] if i < len(lower_values) else None,
                        'upper': upper_values[i] if i < len(upper_values) else None
                    })
        
        return forecast_points
    
    def _create_accuracy_record(self, user_id: str, dataset_id: str, chart_id: str,
                                chart_title: str, forecast_type: str, domain: str,
                                forecast_point: Dict, model_params: Dict) -> bool:
        """Create a forecast accuracy record in backend"""
        try:
            # Calculate target date (when this forecast is for)
            target_date_str = forecast_point['date']
            target_date = datetime.fromisoformat(target_date_str.replace('Z', '+00:00'))
            
            # Payload for backend (datasetId can be empty initially, will be updated later)
            payload = {
                'userId': user_id,
                'datasetId': dataset_id if dataset_id else None,  # Allow empty datasetId
                'chartId': chart_id,
                'chartTitle': chart_title,
                'forecastType': forecast_type,
                'domain': domain,
                'forecastDate': datetime.now().isoformat(),
                'forecastPeriod': 30,  # Default 30 days
                'targetDate': target_date.isoformat(),
                'predictedValue': forecast_point['predicted'],
                'predictedLower': forecast_point.get('lower'),
                'predictedUpper': forecast_point.get('upper'),
                'modelParameters': model_params,
                'status': 'pending'
            }
            
            # Send to backend
            response = requests.post(
                f"{self.backend_url}/api/forecast-accuracy/create",
                json=payload,
                timeout=5
            )
            
            return response.status_code == 200 or response.status_code == 201
            
        except requests.Timeout:
            print(f"⚠️ Timeout creating accuracy record")
            return False
        except requests.RequestException as e:
            print(f"⚠️ Error creating accuracy record: {e}")
            return False
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            return False

# Global instance
forecast_tracker = ForecastAccuracyTracker()

