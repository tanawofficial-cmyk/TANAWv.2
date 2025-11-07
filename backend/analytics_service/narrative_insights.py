"""
TANAW Narrative Insights Generator - Batch Processing
Generates human-readable explanations of analytics findings using GPT with efficient batch processing
"""

import openai
import json
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TANAWNarrativeInsights:
    """
    Generates narrative insights for analytics findings using GPT with batch processing
    """
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Cost-effective model for narrative generation
        self.batch_size = 3  # Process 3 charts per batch
        self.max_retries = 3
        self.feedback_enhancements = None  # Store feedback-based prompt enhancements
    
    def generate_batch_insights(self, charts_data: List[Dict[str, Any]], domain: str = "sales") -> Dict[str, Any]:
        """
        Generate narrative insights for multiple charts using batch processing
        
        Args:
            charts_data: List of chart data
            domain: Business domain
            
        Returns:
            Dict mapping chart_id to insights
        """
        try:
            # Extract chart summaries (compact metrics only)
            chart_summaries = self._extract_chart_summaries(charts_data)
            
            if not chart_summaries:
                return {}
            
            # Process in batches
            batches = self._chunk_charts(chart_summaries, self.batch_size)
            all_insights = {}
            
            for batch in batches:
                try:
                    batch_insights = self._process_batch(batch, domain)
                    all_insights.update(batch_insights)
                except Exception as e:
                    logger.error(f"Batch processing error: {str(e)}")
                    # Fallback for this batch
                    for chart in batch:
                        chart_id = chart['chart_id']
                        all_insights[chart_id] = self._get_fallback_insights(chart['title'], domain)
            
            logger.info(f"Generated batch insights for {len(all_insights)} charts")
            return all_insights
            
        except Exception as e:
            logger.error(f"Error in batch insights generation: {str(e)}")
            return {}
    
    def _extract_chart_summaries(self, charts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract detailed summaries with actual data for GPT analysis"""
        summaries = []
        
        for i, chart in enumerate(charts_data):
            chart_id = chart.get('id', f"chart_{i}")
            title = chart.get('title', 'Analytics Chart')
            chart_type = chart.get('type', 'line')
            data = chart.get('data', {})
            
            # Extract detailed metrics with actual data
            metrics = self._extract_key_metrics(data, chart_type, title)
            
            # Add raw data for specific analysis
            raw_data = {}
            if isinstance(data, dict):
                if 'x' in data and 'y' in data:
                    # Include actual data points for detailed analysis
                    x_values = data.get('x', [])
                    y_values = data.get('y', [])
                    
                    if x_values and y_values:
                        # Create sorted data for analysis
                        sorted_data = sorted(zip(x_values, y_values), key=lambda x: x[1], reverse=True)
                        raw_data = {
                            'data_points': sorted_data[:10],  # Top 10 for analysis
                            'total_data_points': len(x_values),
                            'x_axis_label': 'Product Category' if 'product' in title.lower() else 'Date',
                            'y_axis_label': 'Sales Value (₱)' if 'sales' in title.lower() else 'Value'
                        }
            
            summary = {
                'chart_id': chart_id,
                'title': title,
                'type': chart_type,
                'metrics': metrics,
                'raw_data': raw_data
            }
            
            print(f"📝 Extracted detailed summary for chart {i}: {chart_id} - {title}")
            print(f"📝 Metrics: {metrics}")
            print(f"📝 Raw data points: {len(raw_data.get('data_points', []))} points")
            
            summaries.append(summary)
        
        return summaries
    
    def _extract_key_metrics(self, data: Dict[str, Any], chart_type: str, title: str) -> Dict[str, Any]:
        """Extract detailed metrics for business insights"""
        metrics = {}
        
        if isinstance(data, dict):
            if 'x' in data and 'y' in data:
                x_values = data.get('x', [])
                y_values = data.get('y', [])
                
                if y_values and x_values:
                    # Calculate comprehensive business metrics
                    total_sales = sum(y_values)
                    max_value = max(y_values)
                    min_value = min(y_values)
                    avg_value = total_sales / len(y_values)
                    
                    # Find top and bottom performers
                    sorted_data = sorted(zip(x_values, y_values), key=lambda x: x[1], reverse=True)
                    top_3 = sorted_data[:3]
                    bottom_3 = sorted_data[-3:]
                    
                    # Calculate concentration metrics
                    top_5_sales = sum([item[1] for item in sorted_data[:5]])
                    concentration_ratio = top_5_sales / total_sales if total_sales > 0 else 0
                    
                    # Performance gap
                    performance_gap = max_value / min_value if min_value > 0 else 0
                    
                    metrics.update({
                        'chart_type': chart_type,
                        'total_sales': total_sales,
                        'max_value': max_value,
                        'min_value': min_value,
                        'avg_value': avg_value,
                        'total_products': len(y_values),
                        'top_3_products': [{'name': item[0], 'sales': item[1]} for item in top_3],
                        'bottom_3_products': [{'name': item[0], 'sales': item[1]} for item in bottom_3],
                        'concentration_ratio': concentration_ratio,
                        'performance_gap': performance_gap,
                        'trend': self._calculate_trend(y_values),
                        'pareto_effect': concentration_ratio > 0.8  # 80/20 rule
                    })
            
            # Handle forecast data
            if 'historical' in data and 'forecast' in data:
                hist_y = data['historical'].get('y', [])
                forecast_y = data['forecast'].get('y', [])
                
                if hist_y:
                    hist_avg = sum(hist_y) / len(hist_y)
                    forecast_avg = sum(forecast_y) / len(forecast_y) if forecast_y else 0
                    growth_rate = self._calculate_growth_rate(hist_y, forecast_y)
                    
                    metrics.update({
                        'historical_avg': hist_avg,
                        'forecast_avg': forecast_avg,
                        'growth_rate': growth_rate,
                        'forecast_trend': 'increasing' if growth_rate > 0 else 'decreasing' if growth_rate < 0 else 'stable'
                    })
        
        return metrics
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "stable"
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg * 1.1:
            return "upward"
        elif second_avg < first_avg * 0.9:
            return "downward"
        else:
            return "stable"
    
    def _calculate_growth_rate(self, historical: List[float], forecast: List[float]) -> float:
        """Calculate growth rate between historical and forecast"""
        if not historical or not forecast:
            return 0.0
        
        hist_avg = sum(historical) / len(historical)
        forecast_avg = sum(forecast) / len(forecast)
        
        if hist_avg == 0:
            return 0.0
        
        return ((forecast_avg - hist_avg) / hist_avg) * 100
    
    def _chunk_charts(self, charts: List[Dict], batch_size: int) -> List[List[Dict]]:
        """Split charts into batches"""
        return [charts[i:i + batch_size] for i in range(0, len(charts), batch_size)]
    
    def _process_batch(self, batch: List[Dict], domain: str) -> Dict[str, Any]:
        """Process a single batch of charts"""
        print(f"📝 Processing batch of {len(batch)} charts")
        prompt = self._create_batch_prompt(batch, domain)
        print(f"📝 Batch prompt length: {len(prompt)} characters")
        
        for attempt in range(self.max_retries):
            try:
                print(f"📝 GPT API call attempt {attempt + 1}/{self.max_retries}")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an AI analytics narrator for TANAW, a business analytics platform for SMEs."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                
                insights_text = response.choices[0].message.content.strip()
                print(f"📝 GPT response: {insights_text[:200]}...")
                
                result = self._parse_batch_response(insights_text, batch)
                print(f"📝 Parsed insights: {list(result.keys())}")
                return result
                
            except Exception as e:
                print(f"📝 GPT API error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise e
    
    def set_feedback_enhancements(self, enhancements: Optional[Dict] = None):
        """
        Set feedback-based prompt enhancements (Adaptive Learning Feature)
        This allows the system to learn from user feedback and improve recommendations
        
        Args:
            enhancements: Dict with enhancement instructions from feedback analysis
        """
        self.feedback_enhancements = enhancements
        if enhancements:
            print(f"🧠 Adaptive Learning: Applied {len(enhancements.get('enhancements', []))} feedback-based enhancements")
    
    def _create_batch_prompt(self, batch: List[Dict], domain: str) -> str:
        """Create prompt for business insights - Original defense format"""
        charts_json = json.dumps(batch, separators=(',', ':'))
        
        base_prompt = f"""You are a senior business analyst for TANAW, an SME analytics platform. Analyze each chart and provide clear, actionable insights.

For each chart, provide THREE sections:

1. **WHAT I SEE**: What the data shows - specific numbers, trends, and patterns
2. **MY RECOMMENDATION**: Clear, actionable business recommendations  
3. **POTENTIAL IMPACT**: Expected outcomes and benefits of following the recommendations

Requirements:
- Use EXACT data points, names, and values from the dataset
- Be specific and concise
- Focus on actionable insights for SMEs
- Reference actual products, values, and metrics from the data"""

        # 🧠 ADAPTIVE LEARNING: Add feedback-based enhancements
        if self.feedback_enhancements and self.feedback_enhancements.get('enhancements'):
            base_prompt += "\n\n🎯 **USER FEEDBACK-INFORMED GUIDELINES** (Based on what users found valuable):\n"
            
            for enhancement in self.feedback_enhancements['enhancements']:
                priority_emoji = "🔴" if enhancement['priority'] == 'high' else "🟡" if enhancement['priority'] == 'medium' else "🟢"
                base_prompt += f"{priority_emoji} {enhancement['instruction']}\n"
            
            base_prompt += f"\nConfidence Level: {self.feedback_enhancements.get('confidence', 0):.0%} (based on {self.feedback_enhancements.get('feedbackCount', 0)} user feedback entries)\n"
        
        base_prompt += """

Return ONLY JSON in this exact format:
[
  {{
    "chart_id": "...",
    "what_i_see": "Specific analysis with actual data points and trends",
    "my_recommendation": "Clear, actionable recommendations for business improvement",
    "potential_impact": "Expected outcomes and business benefits",
    "confidence": 0.0-1.0
  }}
]

Charts:
{charts_json}"""
        
        return base_prompt
    
    def _parse_batch_response(self, response_text: str, batch: List[Dict]) -> Dict[str, Any]:
        """Parse enhanced GPT batch response with business recommendations"""
        try:
            # Clean response text
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Try to find the JSON part if it's embedded in text
            if '[' in response_text and ']' in response_text:
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                response_text = response_text[start_idx:end_idx]
            
            insights = json.loads(response_text)
            
            # Convert to defense format dict
            result = {}
            for insight in insights:
                chart_id = insight.get('chart_id')
                if chart_id:
                    # Extract the three main sections (Defense format)
                    what_i_see = insight.get('what_i_see', '')
                    my_recommendation = insight.get('my_recommendation', '')
                    potential_impact = insight.get('potential_impact', '')
                    confidence = insight.get('confidence', 0.8)
                    
                    # Create insights structure with defense format
                    result[chart_id] = {
                        'chart_title': batch[0].get('title', 'Analytics Chart') if batch else 'Chart',
                        'domain': 'sales',  # Could be enhanced to detect domain
                        'what_i_see': what_i_see,
                        'my_recommendation': my_recommendation,
                        'potential_impact': potential_impact,
                        'insights': f"{what_i_see} {my_recommendation}",  # Combined for backward compatibility
                        'key_points': [my_recommendation, potential_impact],  # Key recommendations
                        'confidence': confidence,
                        'generated_at': datetime.now().isoformat(),
                        'insight_type': 'defense_format'
                    }
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            logger.error(f"Response text: {response_text[:500]}...")
            # Fallback: create enhanced insights for each chart in batch
            result = {}
            for chart in batch:
                chart_id = chart['chart_id']
                result[chart_id] = self._get_enhanced_fallback_insights(chart['title'], 'sales')
            return result
            
        except Exception as e:
            logger.error(f"Error parsing enhanced batch response: {str(e)}")
            # Fallback: create enhanced insights for each chart in batch
            result = {}
            for chart in batch:
                chart_id = chart['chart_id']
                result[chart_id] = self._get_enhanced_fallback_insights(chart['title'], 'sales')
            return result
    
    def generate_dashboard_summary(self, charts_data: List[Dict[str, Any]], domain: str = "sales") -> Dict[str, Any]:
        """
        Generate overall dashboard summary insights
        
        Args:
            charts_data: List of all chart data
            domain: Business domain
            
        Returns:
            Dict containing dashboard summary
        """
        try:
            # Extract key metrics from all charts
            summary_data = self._extract_dashboard_metrics(charts_data)
            
            # Create comprehensive prompt
            prompt = self._create_dashboard_prompt(summary_data, domain)
            
            # Call GPT for dashboard summary
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a business consultant providing executive summaries of analytics dashboards for SME owners."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            summary_text = response.choices[0].message.content.strip()
            
            # Structure the enhanced summary
            summary = {
                "executive_overview": self._extract_section(summary_text, "EXECUTIVE OVERVIEW"),
                "strategic_insights": self._extract_section(summary_text, "STRATEGIC INSIGHTS"),
                "immediate_actions": self._extract_section(summary_text, "IMMEDIATE ACTIONS"),
                "strategic_initiatives": self._extract_section(summary_text, "STRATEGIC INITIATIVES"),
                "risk_mitigation": self._extract_section(summary_text, "RISK MITIGATION"),
                "success_framework": self._extract_section(summary_text, "SUCCESS FRAMEWORK"),
                "overview": summary_text,  # Full text for backward compatibility
                "key_findings": self._extract_key_findings(summary_text),
                "recommendations": self._extract_recommendations(summary_text),
                "domain": domain,
                "generated_at": datetime.now().isoformat(),
                "summary_type": "enhanced_executive_summary"
            }
            
            logger.info(f"Generated dashboard summary for {domain} domain")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {str(e)}")
            return self._get_fallback_summary(domain)
    
    def _extract_data_points(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract meaningful data points from chart data - LIMITED for GPT processing"""
        data_points = []
        
        if isinstance(data, dict):
            # Handle forecast data format with historical and forecast
            if 'historical' in data and 'forecast' in data:
                historical = data['historical']
                forecast = data['forecast']
                
                # Add historical data points (LIMITED to first 20 points)
                if 'x' in historical and 'y' in historical:
                    max_points = min(20, len(historical['x']), len(historical['y']))
                    for i in range(max_points):
                        data_points.append({
                            'date': historical['x'][i],
                            'value': historical['y'][i],
                            'type': 'historical'
                        })
                
                # Add forecast data points (LIMITED to first 10 points)
                if 'x' in forecast and 'y' in forecast:
                    max_points = min(10, len(forecast['x']), len(forecast['y']))
                    for i in range(max_points):
                        data_points.append({
                            'date': forecast['x'][i],
                            'value': forecast['y'][i],
                            'type': 'forecast'
                        })
                        
            # Handle simple {x: [...], y: [...]} format
            elif 'x' in data and 'y' in data:
                x_values = data.get('x', [])
                y_values = data.get('y', [])
                
                # LIMIT to first 30 points to avoid token limit
                max_points = min(30, len(x_values), len(y_values))
                for i in range(max_points):
                    data_points.append({
                        'date': x_values[i],
                        'value': y_values[i],
                        'type': 'data'
                    })
                    
            elif isinstance(data, list):
                # Handle array of objects format
                data_points = data[:10]  # Limit to first 10 points for analysis
        
        return data_points
    
    def _create_insights_prompt(self, title: str, chart_type: str, description: str, 
                               data_points: List[Dict], domain: str) -> str:
        """Create GPT prompt for chart insights"""
        
        domain_context = {
            "sales": "retail sales performance and trends",
            "inventory": "inventory management and stock levels", 
            "finance": "financial performance and cash flow",
            "customer": "customer behavior and segmentation"
        }
        
        # Sample data points for analysis (LIMITED to 3 points to save tokens)
        sample_data = data_points[:3] if len(data_points) > 3 else data_points
        
        # Calculate basic statistics for better insights
        if data_points:
            values = [point.get('value', 0) for point in data_points if point.get('value') is not None]
            if values:
                min_val = min(values)
                max_val = max(values)
                avg_val = sum(values) / len(values)
                data_stats = f"Range: {min_val:.0f}-{max_val:.0f}, Avg: {avg_val:.0f}"
            else:
                data_stats = "No numerical data"
        else:
            data_stats = "No data points"
        
        # Create concise prompt to save tokens
        prompt = f"""Analyze this {domain_context.get(domain, 'business')} chart for a small business owner:

Chart: {title} ({chart_type})
Description: {description}
Data: {data_stats} | Points: {len(data_points)}
Sample: {json.dumps(sample_data[:2], separators=(',', ':'))}

Provide:
1. What this chart shows (1 sentence)
2. Key trends (1 sentence with actual numbers)
3. Business meaning (1 sentence)
4. Action recommendation (1 sentence)

Keep each point to 1 sentence. Use business language."""
        
        return prompt
    
    def _create_dashboard_prompt(self, summary_data: Dict, domain: str) -> str:
        """Create enhanced GPT prompt for executive dashboard summary with business recommendations"""
        
        domain_context = {
            "sales": "sales performance and revenue optimization",
            "inventory": "inventory management and supply chain optimization",
            "finance": "financial health and profitability enhancement", 
            "customer": "customer insights and relationship optimization"
        }
        
        prompt = f"""You are a senior business consultant providing an executive summary for a small business owner's {domain_context.get(domain, 'business')} analytics dashboard.

Domain: {domain.title()}
Charts Available: {summary_data.get('chart_count', 0)}
Data Quality: {summary_data.get('data_quality', 'Good')}

Provide a comprehensive executive summary including:

1. **EXECUTIVE OVERVIEW**: High-level business performance summary with key metrics
2. **STRATEGIC INSIGHTS**: Top 3 critical business insights that impact organizational success
3. **IMMEDIATE ACTIONS**: Specific, actionable recommendations for the next 30 days with expected outcomes
4. **STRATEGIC INITIATIVES**: Medium-term opportunities (1-6 months) with ROI projections
5. **RISK MITIGATION**: Areas requiring attention or monitoring with risk levels
6. **SUCCESS FRAMEWORK**: How to measure and track the impact of recommended actions

Focus on:
- Concrete, implementable strategies
- Specific timelines and expected outcomes
- Resource requirements and constraints for SMEs
- Competitive advantages and market opportunities
- Financial impact and growth potential

Write as a strategic business advisor speaking to a busy business owner who needs clear, actionable insights for organizational decision-making."""
        
        return prompt
    
    def _structure_insights(self, insights_text: str, chart_title: str, domain: str) -> Dict[str, Any]:
        """Structure the GPT response into organized insights"""
        
        return {
            "chart_title": chart_title,
            "domain": domain,
            "insights": insights_text,
            "key_points": self._extract_bullet_points(insights_text),
            "confidence": "high",  # GPT-generated insights are generally reliable
            "generated_at": datetime.now().isoformat()
        }
    
    def _extract_bullet_points(self, text: str) -> List[str]:
        """Extract bullet points or key statements from text"""
        lines = text.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or 
                        line.startswith('1.') or line.startswith('2.') or 
                        line.startswith('3.') or line.startswith('4.')):
                bullet_points.append(line)
        
        return bullet_points[:5]  # Limit to top 5 points
    
    def _extract_dashboard_metrics(self, charts_data: List[Dict]) -> Dict[str, Any]:
        """Extract key metrics from all charts"""
        return {
            "chart_count": len(charts_data),
            "data_quality": "Good",  # Could be enhanced with actual data quality assessment
            "chart_types": list(set([chart.get('type', 'unknown') for chart in charts_data])),
            "total_data_points": sum([len(chart.get('data', {}).get('x', [])) for chart in charts_data])
        }
    
    def _extract_key_findings(self, text: str) -> List[str]:
        """Extract key findings from summary text"""
        # Simple extraction - could be enhanced with NLP
        sentences = text.split('.')
        return [s.strip() for s in sentences if len(s.strip()) > 20][:3]
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from summary text"""
        # Look for recommendation keywords
        lines = text.split('\n')
        recommendations = []
        
        for line in lines:
            line = line.strip().lower()
            if any(word in line for word in ['recommend', 'suggest', 'should', 'consider', 'action']):
                recommendations.append(line)
        
        return recommendations[:3]
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from the enhanced summary text"""
        lines = text.split('\n')
        section_content = []
        in_section = False
        
        for line in lines:
            line = line.strip()
            if section_name in line.upper():
                in_section = True
                continue
            elif in_section and line.startswith('**') and line.endswith('**'):
                # Found next section, stop
                break
            elif in_section and line:
                section_content.append(line)
        
        return '\n'.join(section_content) if section_content else ""
    
    def _get_fallback_insights(self, chart_title: str, domain: str) -> Dict[str, Any]:
        """Fallback insights when GPT fails"""
        return {
            "chart_title": chart_title,
            "domain": domain,
            "insights": f"This {chart_title} shows important {domain} metrics for your business. Review the data points to identify trends and patterns.",
            "key_points": [
                "Data visualization helps identify business trends",
                "Regular monitoring of these metrics is important",
                "Consider consulting with a business advisor for deeper analysis"
            ],
            "confidence": "medium",
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_enhanced_fallback_insights(self, chart_title: str, domain: str) -> Dict[str, Any]:
        """Fallback insights with defense format"""
        return {
            "chart_title": chart_title,
            "domain": domain,
            "what_i_see": f"This {chart_title} provides valuable insights into your {domain} performance and business operations.",
            "my_recommendation": f"Analyze the data patterns to identify opportunities and develop a monitoring system for these {domain} metrics.",
            "potential_impact": f"Regular monitoring of {domain} metrics helps identify opportunities and risks early, leading to better informed business decisions.",
            "insights": f"This {chart_title} shows important {domain} metrics for your business. Review the data points to identify trends and patterns.",
            "key_points": [
                f"Analyze data patterns for opportunities",
                f"Monitor {domain} metrics regularly"
            ],
            "confidence": 0.6,
            "generated_at": datetime.now().isoformat(),
            "insight_type": "enhanced_business_recommendations"
        }
    
    def _get_fallback_summary(self, domain: str) -> Dict[str, Any]:
        """Fallback summary when GPT fails"""
        return {
            "overview": f"Your {domain} analytics dashboard provides valuable insights into your business performance. Review the charts to understand key trends and patterns.",
            "key_findings": [
                f"{domain.title()} data shows important business metrics",
                "Regular analysis helps identify opportunities",
                "Data-driven decisions improve business outcomes"
            ],
            "recommendations": [
                "Monitor these metrics regularly",
                "Set up alerts for significant changes",
                "Consider professional consultation for complex analysis"
            ],
            "domain": domain,
            "generated_at": datetime.now().isoformat()
        }
