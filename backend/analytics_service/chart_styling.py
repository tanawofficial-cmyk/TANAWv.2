# chart_styling.py
# TANAW Chart Styling Module

class TANAWChartStyling:
    """Chart styling configuration for TANAW analytics"""
    
    def __init__(self):
        self.colors = {
            'primary': '#3B82F6',
            'secondary': '#10B981',
            'accent': '#F59E0B',
            'danger': '#EF4444',
            'warning': '#F59E0B',
            'info': '#3B82F6',
            'success': '#10B981'
        }
        
        self.chart_styles = {
            'bar': {
                'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                'borderColor': '#3B82F6',
                'borderWidth': 2
            },
            'line': {
                'backgroundColor': 'rgba(16, 185, 129, 0.1)',
                'borderColor': '#10B981',
                'borderWidth': 2,
                'fill': False
            },
            'pie': {
                'backgroundColor': [
                    '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
                    '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
                ]
            }
        }
    
    def get_chart_style(self, chart_type):
        """Get styling configuration for chart type"""
        return self.chart_styles.get(chart_type, self.chart_styles['bar'])
    
    def get_color_scheme(self):
        """Get color scheme for charts"""
        return self.colors
    
    def get_bar_chart_config(self, chart_type="bar", title="Bar Chart", x_label="Category", y_label="Value", **kwargs):
        """Get configuration for bar charts"""
        return {
            'type': chart_type,
            'title': title,
            'x_label': x_label,
            'y_label': y_label,
            'colors': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'],
            'backgroundColor': 'rgba(59, 130, 246, 0.6)',
            'borderColor': '#3B82F6',
            'borderWidth': 2
        }
    
    def get_line_chart_config(self, chart_type="line", title="Line Chart", x_label="X Axis", y_label="Y Axis", **kwargs):
        """Get configuration for line charts"""
        return {
            'type': chart_type,
            'title': title,
            'x_label': x_label,
            'y_label': y_label,
            'line_color': '#10B981',
            'fill_color': 'rgba(16, 185, 129, 0.1)',
            'borderWidth': 2,
            'tension': 0.4
        }
    
    def get_forecast_chart_config(self, chart_type="forecast", title="Forecast", x_label="Date", y_label="Value", **kwargs):
        """Get configuration for forecast charts"""
        return {
            'type': chart_type,
            'title': title,
            'x_label': x_label,
            'y_label': y_label,
            'actual_color': '#3B82F6',
            'forecast_color': '#10B981',
            'confidence_color': 'rgba(16, 185, 129, 0.2)',
            'borderWidth': 2
        }

