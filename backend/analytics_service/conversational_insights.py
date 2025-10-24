"""
TANAW Conversational Narrative Insights Generator
Generates personalized, conversational business insights like talking to a real business analyst
"""

import openai
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class TANAWConversationalInsights:
    """
    Generates conversational, personalized business insights like a real business analyst
    """
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.batch_size = 2  # Smaller batches for more personalized insights
        self.max_retries = 3
        
        # Conversational styles and personalities
        self.analyst_personalities = [
            "experienced retail analyst",
            "seasoned business consultant", 
            "data-driven strategy expert",
            "SME growth specialist",
            "operations optimization consultant"
        ]
        
        # Conversation starters
        self.conversation_starters = [
            "Looking at your data, I can see some interesting patterns emerging...",
            "I've analyzed your business metrics and here's what stands out to me...",
            "Your data tells a compelling story about your business performance...",
            "After diving deep into your numbers, I have some insights to share...",
            "I notice some fascinating trends in your business data that we should discuss..."
        ]
    
    def generate_conversational_insights(self, charts_data: List[Dict[str, Any]], domain: str = "sales") -> Dict[str, Any]:
        """
        Generate conversational, personalized insights for charts
        
        Args:
            charts_data: List of chart data
            domain: Business domain
            
        Returns:
            Dict mapping chart_id to conversational insights
        """
        try:
            # Extract chart summaries with rich context
            chart_summaries = self._extract_rich_chart_summaries(charts_data)
            
            if not chart_summaries:
                return {}
            
            # Process in smaller batches for more personalized insights
            batches = self._chunk_charts(chart_summaries, self.batch_size)
            all_insights = {}
            
            for batch in batches:
                print(f"🗣️ Generating conversational insights for batch of {len(batch)} charts")
                
                # Generate insights for this batch
                batch_insights = self._generate_batch_conversational_insights(batch, domain)
                all_insights.update(batch_insights)
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
            
            return all_insights
            
        except Exception as e:
            print(f"❌ Error generating conversational insights: {e}")
            return {}
    
    def _extract_rich_chart_summaries(self, charts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract rich, contextual summaries for conversational analysis"""
        summaries = []
        
        for i, chart in enumerate(charts_data):
            chart_id = chart.get('id', f'chart_{i}')
            title = chart.get('title', 'Analytics Chart')
            chart_type = chart.get('type', 'bar')
            data = chart.get('data', {})
            
            # Extract rich business context
            business_context = self._extract_business_context(data, chart_type, title)
            
            # Create comprehensive summary
            summary = {
                'chart_id': chart_id,
                'title': title,
                'type': chart_type,
                'business_context': business_context,
                'raw_data': data,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            print(f"🗣️ Extracted rich context for {chart_id}: {title}")
            summaries.append(summary)
        
        return summaries
    
    def _extract_business_context(self, data: Dict[str, Any], chart_type: str, title: str) -> Dict[str, Any]:
        """Extract rich business context for conversational analysis"""
        context = {
            'chart_type': chart_type,
            'title': title,
            'data_quality': 'high',
            'business_metrics': {},
            'performance_indicators': {},
            'trend_analysis': {},
            'opportunities': [],
            'concerns': []
        }
        
        if isinstance(data, dict):
            if 'x' in data and 'y' in data:
                x_values = data.get('x', [])
                y_values = data.get('y', [])
                
                if y_values and x_values:
                    # Rich business metrics
                    total_value = sum(y_values)
                    max_value = max(y_values)
                    min_value = min(y_values)
                    avg_value = total_value / len(y_values)
                    
                    # Performance analysis
                    sorted_data = sorted(zip(x_values, y_values), key=lambda x: x[1], reverse=True)
                    top_performer = sorted_data[0] if sorted_data else None
                    bottom_performer = sorted_data[-1] if sorted_data else None
                    
                    # Calculate business ratios
                    performance_gap = max_value / min_value if min_value > 0 else 0
                    concentration_ratio = sum([item[1] for item in sorted_data[:3]]) / total_value if total_value > 0 else 0
                    
                    # Trend analysis
                    trend_direction = self._analyze_trend(y_values)
                    volatility = self._calculate_volatility(y_values)
                    
                    context.update({
                        'business_metrics': {
                            'total_value': total_value,
                            'average_value': avg_value,
                            'max_value': max_value,
                            'min_value': min_value,
                            'total_items': len(y_values)
                        },
                        'performance_indicators': {
                            'top_performer': {'name': top_performer[0], 'value': top_performer[1]} if top_performer else None,
                            'bottom_performer': {'name': bottom_performer[0], 'value': bottom_performer[1]} if bottom_performer else None,
                            'performance_gap': performance_gap,
                            'concentration_ratio': concentration_ratio
                        },
                        'trend_analysis': {
                            'direction': trend_direction,
                            'volatility': volatility,
                            'stability': 'high' if volatility < 0.2 else 'medium' if volatility < 0.5 else 'low'
                        }
                    })
                    
                    # Identify opportunities and concerns
                    if concentration_ratio > 0.7:
                        context['concerns'].append("High concentration risk - over-reliance on top performers")
                    if performance_gap > 10:
                        context['opportunities'].append("Significant performance gap - potential for improvement")
                    if volatility > 0.5:
                        context['concerns'].append("High volatility - inconsistent performance")
            
            # Handle forecast data
            if 'historical' in data and 'forecast' in data:
                hist_y = data['historical'].get('y', [])
                forecast_y = data['forecast'].get('y', [])
                
                if hist_y and forecast_y:
                    hist_avg = sum(hist_y) / len(hist_y)
                    forecast_avg = sum(forecast_y) / len(forecast_y)
                    growth_rate = ((forecast_avg - hist_avg) / hist_avg * 100) if hist_avg > 0 else 0
                    
                    context['forecast_analysis'] = {
                        'historical_average': hist_avg,
                        'forecast_average': forecast_avg,
                        'growth_rate': growth_rate,
                        'trend': 'growing' if growth_rate > 5 else 'declining' if growth_rate < -5 else 'stable'
                    }
        
        return context
    
    def _analyze_trend(self, values: List[float]) -> str:
        """Analyze trend direction with more nuance"""
        if len(values) < 3:
            return "insufficient_data"
        
        # Use linear regression for trend analysis
        n = len(values)
        x = list(range(n))
        y = values
        
        # Calculate slope
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return "strong_upward"
        elif slope > 0.05:
            return "moderate_upward"
        elif slope > -0.05:
            return "stable"
        elif slope > -0.1:
            return "moderate_downward"
        else:
            return "strong_downward"
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility as coefficient of variation"""
        if not values or len(values) < 2:
            return 0.0
        
        mean_val = sum(values) / len(values)
        if mean_val == 0:
            return 0.0
        
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        return std_dev / mean_val
    
    def _chunk_charts(self, charts: List[Dict], batch_size: int) -> List[List[Dict]]:
        """Split charts into smaller batches for personalized processing"""
        return [charts[i:i + batch_size] for i in range(0, len(charts), batch_size)]
    
    def _generate_batch_conversational_insights(self, batch: List[Dict], domain: str) -> Dict[str, Any]:
        """Generate conversational insights for a batch of charts"""
        try:
            # Create personalized prompt
            prompt = self._create_conversational_prompt(batch, domain)
            
            print(f"🗣️ Generating conversational insights for {len(batch)} charts")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior business analyst providing personalized, conversational insights to a business owner. Be warm, professional, and insightful. Use specific data points and provide actionable advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Slightly higher for more conversational tone
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content
            return self._parse_conversational_response(response_text, batch)
            
        except Exception as e:
            print(f"❌ Error generating conversational insights: {e}")
            return {}
    
    def _create_conversational_prompt(self, batch: List[Dict], domain: str) -> str:
        """Create conversational prompt for personalized business insights"""
        # Select random analyst personality
        personality = random.choice(self.analyst_personalities)
        starter = random.choice(self.conversation_starters)
        
        charts_json = json.dumps(batch, separators=(',', ':'))
        
        return f"""You are a {personality} having a one-on-one consultation with a business owner. {starter}

Analyze each chart and provide personalized, conversational insights as if you're sitting across from them discussing their business.

For each chart, provide:

1. **CONVERSATIONAL ANALYSIS**: A natural, conversational explanation of what the data shows, using specific numbers and names from their business
2. **PERSONALIZED INSIGHTS**: What this means specifically for their business, with concrete examples
3. **ACTIONABLE ADVICE**: Specific, practical recommendations they can implement, with realistic timelines
4. **BUSINESS IMPACT**: How these insights can help grow their business or solve problems

Guidelines:
- Write like you're talking to them directly ("I can see that...", "What's interesting is...", "This suggests...")
- Use their actual data points, product names, and numbers
- Be specific and concrete, not generic
- Show genuine business expertise and insight
- Make recommendations that are realistic for their business size
- Reference specific products, regions, or metrics from their data
- Be encouraging but honest about challenges
- Focus on actionable insights that will make a real difference

Return ONLY JSON in this exact format:
[
  {{
    "chart_id": "...",
    "conversational_analysis": "Natural, conversational explanation of what the data shows with specific details",
    "personalized_insights": "What this means specifically for their business with concrete examples",
    "actionable_advice": "Specific, practical recommendations with realistic timelines",
    "business_impact": "How these insights can help grow their business or solve problems",
    "confidence": 0.0-1.0
  }}
]

Charts to analyze:
{charts_json}"""
    
    def _parse_conversational_response(self, response_text: str, batch: List[Dict]) -> Dict[str, Any]:
        """Parse conversational GPT response"""
        try:
            # Clean response text
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Extract JSON if embedded
            if '[' in response_text and ']' in response_text:
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                response_text = response_text[start_idx:end_idx]
            
            insights = json.loads(response_text)
            
            # Convert to conversational format
            result = {}
            for insight in insights:
                chart_id = insight.get('chart_id')
                if chart_id:
                    result[chart_id] = {
                        'chart_title': next((chart['title'] for chart in batch if chart['chart_id'] == chart_id), 'Analytics Chart'),
                        'domain': 'business',
                        'conversational_analysis': insight.get('conversational_analysis', ''),
                        'personalized_insights': insight.get('personalized_insights', ''),
                        'actionable_advice': insight.get('actionable_advice', ''),
                        'business_impact': insight.get('business_impact', ''),
                        'confidence': insight.get('confidence', 0.8),
                        'generated_at': datetime.now().isoformat(),
                        'insight_type': 'conversational'
                    }
            
            return result
            
        except Exception as e:
            print(f"❌ Error parsing conversational response: {e}")
            return {}
    
    def generate_dashboard_summary(self, summary_data: Dict, domain: str) -> Dict[str, Any]:
        """Generate conversational dashboard summary"""
        try:
            prompt = self._create_dashboard_summary_prompt(summary_data, domain)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior business analyst providing a comprehensive business review. Be conversational, insightful, and focus on actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return {
                'summary': response.choices[0].message.content,
                'generated_at': datetime.now().isoformat(),
                'type': 'conversational_dashboard'
            }
            
        except Exception as e:
            print(f"❌ Error generating dashboard summary: {e}")
            return {'summary': 'Unable to generate summary', 'type': 'error'}
    
    def _create_dashboard_summary_prompt(self, summary_data: Dict, domain: str) -> str:
        """Create conversational dashboard summary prompt"""
        personality = random.choice(self.analyst_personalities)
        
        return f"""You are a {personality} providing a comprehensive business review to a business owner.

Based on their analytics data, provide a conversational executive summary that:

1. **OVERALL BUSINESS HEALTH**: Give them a clear picture of how their business is performing
2. **KEY STRENGTHS**: Highlight what's working well with specific examples
3. **OPPORTUNITIES**: Identify the biggest opportunities for growth or improvement
4. **PRIORITY ACTIONS**: Recommend the top 3-5 things they should focus on
5. **BUSINESS OUTLOOK**: Share your professional assessment of their business trajectory

Be conversational, encouraging, and specific. Use their actual data and metrics. Focus on actionable insights that will make a real difference to their business.

Data Summary:
{json.dumps(summary_data, separators=(',', ':'))}"""
