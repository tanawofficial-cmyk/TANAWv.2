"""
TANAW Chart Styling Configuration
Professional chart styling with enhanced visuals and proper label handling
"""

from typing import Dict, Any, Optional

class TANAWChartStyling:
    """
    Professional chart styling configurations for TANAW
    Handles overlapping labels, improves visual appeal, and ensures consistency
    """
    
    def __init__(self):
        # Color schemes for different chart types
        self.color_schemes = {
            "sales": {
                "primary": "rgba(59, 130, 246, 0.8)",      # Blue
                "primary_border": "rgba(59, 130, 246, 1)",
                "secondary": "rgba(16, 185, 129, 0.8)",    # Green
                "secondary_border": "rgba(16, 185, 129, 1)",
                "accent": "rgba(245, 158, 11, 0.8)",        # Amber
                "accent_border": "rgba(245, 158, 11, 1)"
            },
            "inventory": {
                "primary": "rgba(139, 69, 19, 0.8)",       # Brown
                "primary_border": "rgba(139, 69, 19, 1)",
                "secondary": "rgba(34, 197, 94, 0.8)",     # Green
                "secondary_border": "rgba(34, 197, 94, 1)",
                "accent": "rgba(239, 68, 68, 0.8)",        # Red
                "accent_border": "rgba(239, 68, 68, 1)"
            },
            "forecast": {
                "primary": "rgba(99, 102, 241, 0.8)",      # Indigo
                "primary_border": "rgba(99, 102, 241, 1)",
                "secondary": "rgba(168, 85, 247, 0.8)",    # Purple
                "secondary_border": "rgba(168, 85, 247, 1)",
                "accent": "rgba(236, 72, 153, 0.8)",       # Pink
                "accent_border": "rgba(236, 72, 153, 1)"
            }
        }
    
    def get_bar_chart_config(self, chart_type: str = "sales", x_label: str = "Category", y_label: str = "Value") -> Dict[str, Any]:
        """
        Get enhanced bar chart configuration
        
        Args:
            chart_type: Type of chart (sales, inventory, forecast)
            x_label: X-axis label
            y_label: Y-axis label
            
        Returns:
            Enhanced chart configuration
        """
        colors = self.color_schemes.get(chart_type, self.color_schemes["sales"])
        
        return {
            "maintainAspectRatio": False,
            "responsive": True,
            "plugins": {
                "legend": {
                    "display": True,
                    "position": "top",
                    "labels": {
                        "usePointStyle": True,
                        "padding": 20,
                        "font": {
                            "size": 12,
                            "weight": "500",
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#374151"
                    }
                },
                "tooltip": {
                    "enabled": True,
                    "mode": "index",
                    "intersect": False,
                    "backgroundColor": "rgba(17, 24, 39, 0.95)",
                    "titleColor": "#ffffff",
                    "bodyColor": "#ffffff",
                    "borderColor": "rgba(255, 255, 255, 0.2)",
                    "borderWidth": 1,
                    "cornerRadius": 12,
                    "displayColors": True,
                    "titleFont": {
                        "size": 13,
                        "weight": "bold",
                        "family": "'Inter', 'Segoe UI', sans-serif"
                    },
                    "bodyFont": {
                        "size": 12,
                        "family": "'Inter', 'Segoe UI', sans-serif"
                    },
                    "padding": 16,
                    "titleSpacing": 8,
                    "bodySpacing": 6
                }
            },
            "scales": {
                "x": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": x_label,
                        "font": {
                            "size": 14,
                            "weight": "600",
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#1F2937"
                    },
                    "grid": {
                        "display": True,
                        "color": "rgba(0, 0, 0, 0.05)",
                        "drawBorder": False,
                        "drawOnChartArea": True,
                        "drawTicks": False
                    },
                    "ticks": {
                        "maxRotation": 45,
                        "minRotation": 0,
                        "font": {
                            "size": 11,
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#6B7280",
                        "padding": 12,
                        "maxTicksLimit": 10
                    },
                    "border": {
                        "display": False
                    }
                },
                "y": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": y_label,
                        "font": {
                            "size": 14,
                            "weight": "600",
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#1F2937"
                    },
                    "grid": {
                        "display": True,
                        "color": "rgba(0, 0, 0, 0.05)",
                        "drawBorder": False,
                        "drawOnChartArea": True,
                        "drawTicks": False
                    },
                    "ticks": {
                        "font": {
                            "size": 11,
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#6B7280",
                        "padding": 12,
                        "callback": "function(value) { return value.toLocaleString(); }"
                    },
                    "border": {
                        "display": False
                    }
                }
            },
            "elements": {
                "bar": {
                    "borderRadius": 6,
                    "borderSkipped": False,
                    "backgroundColor": colors["primary"],
                    "borderColor": colors["primary_border"],
                    "borderWidth": 2
                }
            },
            "animation": {
                "duration": 1200,
                "easing": "easeInOutQuart",
                "delay": 0
            },
            "interaction": {
                "mode": "index",
                "intersect": False
            },
            "layout": {
                "padding": {
                    "top": 20,
                    "bottom": 20,
                    "left": 20,
                    "right": 20
                }
            }
        }
    
    def get_line_chart_config(self, chart_type: str = "sales", x_label: str = "Date", y_label: str = "Value") -> Dict[str, Any]:
        """
        Get enhanced line chart configuration
        
        Args:
            chart_type: Type of chart (sales, inventory, forecast)
            x_label: X-axis label
            y_label: Y-axis label
            
        Returns:
            Enhanced line chart configuration
        """
        colors = self.color_schemes.get(chart_type, self.color_schemes["sales"])
        
        return {
            "maintainAspectRatio": False,
            "responsive": True,
            "plugins": {
                "legend": {
                    "display": True,
                    "position": "top",
                    "labels": {
                        "usePointStyle": True,
                        "padding": 20,
                        "font": {
                            "size": 12,
                            "weight": "500",
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#374151"
                    }
                },
                "tooltip": {
                    "enabled": True,
                    "mode": "index",
                    "intersect": False,
                    "backgroundColor": "rgba(17, 24, 39, 0.95)",
                    "titleColor": "#ffffff",
                    "bodyColor": "#ffffff",
                    "borderColor": "rgba(255, 255, 255, 0.2)",
                    "borderWidth": 1,
                    "cornerRadius": 12,
                    "displayColors": True,
                    "titleFont": {
                        "size": 13,
                        "weight": "bold",
                        "family": "'Inter', 'Segoe UI', sans-serif"
                    },
                    "bodyFont": {
                        "size": 12,
                        "family": "'Inter', 'Segoe UI', sans-serif"
                    },
                    "padding": 16
                }
            },
            "scales": {
                "x": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": x_label,
                        "font": {
                            "size": 14,
                            "weight": "600",
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#1F2937"
                    },
                    "grid": {
                        "display": True,
                        "color": "rgba(0, 0, 0, 0.05)",
                        "drawBorder": False
                    },
                    "ticks": {
                        "font": {
                            "size": 11,
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#6B7280",
                        "padding": 12
                    }
                },
                "y": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": y_label,
                        "font": {
                            "size": 14,
                            "weight": "600",
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#1F2937"
                    },
                    "grid": {
                        "display": True,
                        "color": "rgba(0, 0, 0, 0.05)",
                        "drawBorder": False
                    },
                    "ticks": {
                        "font": {
                            "size": 11,
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#6B7280",
                        "padding": 12,
                        "callback": "function(value) { return value.toLocaleString(); }"
                    }
                }
            },
            "elements": {
                "line": {
                    "borderWidth": 3,
                    "borderColor": colors["primary"],
                    "backgroundColor": colors["primary"],
                    "tension": 0.4
                },
                "point": {
                    "radius": 6,
                    "hoverRadius": 8,
                    "backgroundColor": colors["primary"],
                    "borderColor": "#ffffff",
                    "borderWidth": 2
                }
            },
            "animation": {
                "duration": 1200,
                "easing": "easeInOutQuart"
            },
            "interaction": {
                "mode": "index",
                "intersect": False
            }
        }
    
    def get_forecast_chart_config(self, chart_type: str = "forecast", x_label: str = "Date", y_label: str = "Value") -> Dict[str, Any]:
        """
        Get enhanced forecast chart configuration with confidence intervals
        
        Args:
            chart_type: Type of chart (sales, inventory, forecast)
            x_label: X-axis label
            y_label: Y-axis label
            
        Returns:
            Enhanced forecast chart configuration
        """
        colors = self.color_schemes.get(chart_type, self.color_schemes["forecast"])
        
        return {
            "maintainAspectRatio": False,
            "responsive": True,
            "plugins": {
                "legend": {
                    "display": True,
                    "position": "top",
                    "labels": {
                        "usePointStyle": True,
                        "padding": 20,
                        "font": {
                            "size": 12,
                            "weight": "500",
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#374151"
                    }
                },
                "tooltip": {
                    "enabled": True,
                    "mode": "index",
                    "intersect": False,
                    "backgroundColor": "rgba(17, 24, 39, 0.95)",
                    "titleColor": "#ffffff",
                    "bodyColor": "#ffffff",
                    "borderColor": "rgba(255, 255, 255, 0.2)",
                    "borderWidth": 1,
                    "cornerRadius": 12,
                    "displayColors": True,
                    "titleFont": {
                        "size": 13,
                        "weight": "bold",
                        "family": "'Inter', 'Segoe UI', sans-serif"
                    },
                    "bodyFont": {
                        "size": 12,
                        "family": "'Inter', 'Segoe UI', sans-serif"
                    },
                    "padding": 16
                }
            },
            "scales": {
                "x": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": x_label,
                        "font": {
                            "size": 14,
                            "weight": "600",
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#1F2937"
                    },
                    "grid": {
                        "display": True,
                        "color": "rgba(0, 0, 0, 0.05)",
                        "drawBorder": False
                    },
                    "ticks": {
                        "font": {
                            "size": 11,
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#6B7280",
                        "padding": 12
                    }
                },
                "y": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": y_label,
                        "font": {
                            "size": 14,
                            "weight": "600",
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#1F2937"
                    },
                    "grid": {
                        "display": True,
                        "color": "rgba(0, 0, 0, 0.05)",
                        "drawBorder": False
                    },
                    "ticks": {
                        "font": {
                            "size": 11,
                            "family": "'Inter', 'Segoe UI', sans-serif"
                        },
                        "color": "#6B7280",
                        "padding": 12,
                        "callback": "function(value) { return value.toLocaleString(); }"
                    }
                }
            },
            "elements": {
                "line": {
                    "borderWidth": 3,
                    "tension": 0.4
                },
                "point": {
                    "radius": 5,
                    "hoverRadius": 7
                }
            },
            "animation": {
                "duration": 1500,
                "easing": "easeInOutQuart"
            },
            "interaction": {
                "mode": "index",
                "intersect": False
            }
        }
    
    def get_multi_color_scheme(self, data_length: int, chart_type: str = "sales") -> list:
        """
        Generate a multi-color scheme for charts with multiple data series
        
        Args:
            data_length: Number of data points
            chart_type: Type of chart
            
        Returns:
            List of colors for the data series
        """
        base_colors = self.color_schemes.get(chart_type, self.color_schemes["sales"])
        
        # Generate a gradient of colors
        colors = []
        for i in range(data_length):
            # Create a gradient from primary to secondary colors
            ratio = i / max(1, data_length - 1)
            if ratio < 0.5:
                # Blend primary with accent
                alpha = 0.8 - (ratio * 0.3)
                colors.append(f"rgba(59, 130, 246, {alpha})")
            else:
                # Blend accent with secondary
                alpha = 0.5 + ((ratio - 0.5) * 0.3)
                colors.append(f"rgba(16, 185, 129, {alpha})")
        
        return colors
