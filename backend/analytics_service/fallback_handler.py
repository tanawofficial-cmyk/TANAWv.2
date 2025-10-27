# fallback_handler.py
# Fallback Handler for TANAW Analytics

class TANAWFallbackHandler:
    """Handles fallback operations when primary services fail"""
    
    def __init__(self):
        self.fallback_enabled = True
        self.log_errors = True
    
    def handle_analysis_fallback(self, error_message):
        """Handle analysis fallback when primary analysis fails"""
        if self.log_errors:
            print(f"⚠️ Analysis fallback triggered: {error_message}")
        
        return {
            'success': False,
            'message': 'Analysis temporarily unavailable. Please try again later.',
            'fallback': True,
            'error': str(error_message)
        }
    
    def handle_chart_fallback(self, error_message):
        """Handle chart generation fallback"""
        if self.log_errors:
            print(f"⚠️ Chart fallback triggered: {error_message}")
        
        return {
            'success': False,
            'message': 'Chart generation temporarily unavailable.',
            'fallback': True,
            'error': str(error_message)
        }
    
    def is_fallback_enabled(self):
        """Check if fallback is enabled"""
        return self.fallback_enabled
    
    def enable_fallback(self):
        """Enable fallback handling"""
        self.fallback_enabled = True
    
    def disable_fallback(self):
        """Disable fallback handling"""
        self.fallback_enabled = False
    
    def handle_bar_chart_fallback(self, df, chart_type, generation_func, *args, **kwargs):
        """Handle bar chart generation fallback"""
        try:
            return generation_func(df, *args, **kwargs)
        except Exception as e:
            if self.log_errors:
                print(f"⚠️ Bar chart fallback for {chart_type}: {e}")
            return None
    
    def handle_line_chart_fallback(self, df, chart_type, generation_func, *args, **kwargs):
        """Handle line chart generation fallback"""
        try:
            return generation_func(df, *args, **kwargs)
        except Exception as e:
            if self.log_errors:
                print(f"⚠️ Line chart fallback for {chart_type}: {e}")
            return None
    
    def handle_forecast_fallback(self, df, chart_type, generation_func, *args, **kwargs):
        """Handle forecast generation fallback"""
        try:
            return generation_func(df, *args, **kwargs)
        except Exception as e:
            if self.log_errors:
                print(f"⚠️ Forecast fallback for {chart_type}: {e}")
            return None

