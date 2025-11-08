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
        self.feedback_enhancements = None  # Store feedback-based prompt enhancements
        
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
    
    def set_feedback_enhancements(self, enhancements: Optional[Dict] = None):
        """
        Set feedback-based prompt enhancements (Adaptive Learning Feature)
        This allows the system to learn from user feedback and improve recommendations
        
        Args:
            enhancements: Dict with enhancement instructions from feedback analysis
        """
        self.feedback_enhancements = enhancements
        if enhancements:
            print(f"🧠 Adaptive Learning (Conversational): Applied {len(enhancements.get('enhancements', []))} feedback-based enhancements")
    
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
            
            # Create comprehensive summary (exclude raw_data to keep prompt manageable)
            summary = {
                'chart_id': chart_id,
                'title': title,
                'type': chart_type,
                'business_context': business_context,
                # raw_data excluded - only send business_context metrics to GPT
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
                    
                    # 🎯 ENHANCED: Add strategic data samples for GPT to reference specific examples
                    data_samples = {
                        'top_5_performers': sorted_data[:5] if len(sorted_data) >= 5 else sorted_data,
                        'bottom_5_performers': sorted_data[-5:] if len(sorted_data) >= 5 else [],
                        'recent_10_points': list(zip(x_values[-10:], y_values[-10:])) if len(x_values) >= 10 else list(zip(x_values, y_values))
                    }
                    
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
                        },
                        'data_samples': data_samples  # 🎯 NEW: Strategic samples for GPT
                    })
                    
                    # Identify opportunities and concerns
                    if concentration_ratio > 0.7:
                        context['concerns'].append("High concentration risk - over-reliance on top performers")
                    if performance_gap > 10:
                        context['opportunities'].append("Significant performance gap - potential for improvement")
                    if volatility > 0.5:
                        context['concerns'].append("High volatility - inconsistent performance")
            
        # 🎯 Handle forecast data (list format: [{x, y, type}, ...])
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            # Separate historical and forecast points
            historical_points = [p for p in data if p.get('type') == 'historical']
            forecast_points = [p for p in data if p.get('type') == 'forecast']
            
            if historical_points and forecast_points:
                hist_values = [p.get('y', 0) for p in historical_points]
                forecast_values = [p.get('y', 0) for p in forecast_points]
                
                hist_avg = sum(hist_values) / len(hist_values) if hist_values else 0
                forecast_avg = sum(forecast_values) / len(forecast_values) if forecast_values else 0
                growth_rate = ((forecast_avg - hist_avg) / hist_avg * 100) if hist_avg > 0 else 0
                
                # 🎯 ENHANCED: Add forecast data samples
                forecast_samples = {
                    'recent_5_historical': historical_points[-5:] if len(historical_points) >= 5 else historical_points,
                    'first_5_forecast': forecast_points[:5] if len(forecast_points) >= 5 else forecast_points,
                    'last_5_forecast': forecast_points[-5:] if len(forecast_points) >= 5 else []
                }
                
                context.update({
                    'forecast_analysis': {
                        'historical_average': hist_avg,
                        'forecast_average': forecast_avg,
                        'growth_rate': growth_rate,
                        'trend': 'growing' if growth_rate > 5 else 'declining' if growth_rate < -5 else 'stable',
                        'historical_periods': len(historical_points),
                        'forecast_periods': len(forecast_points)
                    },
                    'data_samples': forecast_samples  # 🎯 NEW: Forecast-specific samples
                })
        
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
            print(f"🗣️ Prompt length: {len(prompt)} characters")
            print(f"🗣️ Prompt preview: {prompt[:500]}...")
            print(f"🗣️ FULL PROMPT:")
            print(prompt)
            print(f"🗣️ END OF PROMPT")
            
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
            print(f"🗣️ GPT Response received: {len(response_text)} characters")
            print(f"🗣️ GPT Response preview: {response_text[:500]}...")
            parsed_result = self._parse_conversational_response(response_text, batch)
            print(f"🗣️ Parsed result: {len(parsed_result)} insights extracted")
            return parsed_result
            
        except Exception as e:
            print(f"❌ Error generating conversational insights: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _create_conversational_prompt(self, batch: List[Dict], domain: str) -> str:
        """Create conversational prompt for personalized business insights"""
        # Select random analyst personality
        personality = random.choice(self.analyst_personalities)
        starter = random.choice(self.conversation_starters)
        
        charts_json = json.dumps(batch, separators=(',', ':'))
        
        prompt_start = f"""You are a {personality} having a one-on-one consultation with a business owner. {starter}

Analyze each chart and provide personalized, conversational insights as if you're sitting across from them discussing their business.

For each chart, provide:

1. **CONVERSATIONAL ANALYSIS**: A natural, conversational explanation of what the data shows, using specific numbers and names from their business
2. **PERSONALIZED INSIGHTS**: What this means specifically for their business, with concrete examples
3. **ACTIONABLE ADVICE**: Specific, practical recommendations they can implement, with realistic timelines
4. **BUSINESS IMPACT**: How these insights can help grow their business or solve problems

Guidelines:
- Write like you're talking to them directly ("I can see that...", "What's interesting is...", "This suggests...")
- Use their actual data points, product names, and numbers from the data_samples provided
- Reference specific examples: "For instance, your Sandwich product sold ₱65,820..." or "Looking at March 1st specifically..."
- Be specific and concrete, not generic
- Show genuine business expertise and insight
- Make recommendations that are realistic for their business size
- Reference specific products, dates, regions, or metrics from their data_samples
- Be encouraging but honest about challenges
- Focus on actionable insights that will make a real difference

**IMPORTANT**: Each chart includes 'data_samples' with specific examples:

For BAR/LINE charts:
- top_5_performers: Best performing items/dates with actual values
- bottom_5_performers: Worst performing items/dates with actual values  
- recent_10_points: Most recent data points to reference current trends

For FORECAST charts:
- recent_5_historical: Last 5 historical data points before forecast
- first_5_forecast: First 5 predicted values (near-term forecast)
- last_5_forecast: Last 5 predicted values (long-term forecast)

Use these samples to provide SPECIFIC examples in your analysis! Reference actual dates, products, and values!"""

        # 🧠 ADAPTIVE LEARNING: Add feedback-based enhancements
        base_prompt = prompt_start
        if self.feedback_enhancements and self.feedback_enhancements.get('enhancements'):
            base_prompt += "\n\n🎯 **USER FEEDBACK-INFORMED TONE** (Based on what users appreciated):\n"
            
            for enhancement in self.feedback_enhancements['enhancements']:
                priority_emoji = "🔴" if enhancement['priority'] == 'high' else "🟡" if enhancement['priority'] == 'medium' else "🟢"
                base_prompt += f"{priority_emoji} {enhancement['instruction']}\n"
            
            base_prompt += f"\nConfidence: {self.feedback_enhancements.get('confidence', 0):.0%}\n"
        
        # ✅ FIX: Use f-string to actually insert the charts_json data
        base_prompt += f"""
Return ONLY JSON in this exact format:
[
  {{{{
    "chart_id": "...",
    "conversational_analysis": "Natural, conversational explanation of what the data shows with specific details",
    "personalized_insights": "What this means specifically for their business with concrete examples",
    "actionable_advice": "Specific, practical recommendations with realistic timelines",
    "business_impact": "How these insights can help grow their business or solve problems",
    "confidence": 0.0-1.0
  }}}}
]

Charts to analyze:
{charts_json}"""
        
        return base_prompt
    
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
            
            print(f"🗣️ Parsed JSON: {len(insights)} insights found")
            print(f"🗣️ Batch chart IDs: {[chart.get('chart_id', 'NO_ID') for chart in batch]}")
            
            # Convert to conversational format
            result = {}
            for i, insight in enumerate(insights):
                chart_id = insight.get('chart_id')
                print(f"🗣️ Processing insight {i}: chart_id='{chart_id}'")
                
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
                else:
                    print(f"⚠️ Skipping insight {i}: No chart_id found in GPT response")
            
            print(f"🗣️ Final result: {len(result)} insights mapped successfully")
            print(f"🗣️ Result keys: {list(result.keys())}")
            return result
            
        except Exception as e:
            print(f"❌ Error parsing conversational response: {e}")
            print(f"❌ Response text that failed to parse: {response_text[:500]}...")
            import traceback
            traceback.print_exc()
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
