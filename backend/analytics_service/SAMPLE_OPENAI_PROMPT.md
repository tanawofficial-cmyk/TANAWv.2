# Sample Data Sent to OpenAI for Narrative Insights

## Overview
This document shows exactly what data TANAW sends to OpenAI's GPT-4o-mini for generating narrative insights and business recommendations.

---

## 1. Chart Data Structure (Before Processing)

This is what a chart looks like when it comes from the chart generators:

```json
{
  "id": "product_comparison_analysis",
  "title": "Product Comparison by Sales",
  "type": "bar",
  "description": "Compares sales across different products",
  "data": {
    "x": ["Product 1089", "Product 1048", "Product 1024", "Product 1003", "Product 1078", "Product 1041", "Product 1043"],
    "y": [220000, 180000, 175000, 150000, 120000, 60000, 55000]
  }
}
```

---

## 2. Extracted Metrics (What We Calculate)

Before sending to OpenAI, we calculate these metrics from the chart data:

```json
{
  "chart_type": "bar",
  "total_sales": 960000,
  "max_value": 220000,
  "min_value": 55000,
  "avg_value": 137142.86,
  "total_products": 7,
  "top_3_products": [
    {"name": "Product 1089", "sales": 220000},
    {"name": "Product 1048", "sales": 180000},
    {"name": "Product 1024", "sales": 175000}
  ],
  "bottom_3_products": [
    {"name": "Product 1078", "sales": 120000},
    {"name": "Product 1041", "sales": 60000},
    {"name": "Product 1043", "sales": 55000}
  ],
  "concentration_ratio": 0.75,
  "performance_gap": 4.0,
  "trend": "upward",
  "pareto_effect": false
}
```

---

## 3. Chart Summary Sent to OpenAI

This is the structured data we send in the prompt:

```json
[
  {
    "chart_id": "product_comparison_analysis",
    "title": "Product Comparison by Sales",
    "type": "bar",
    "metrics": {
      "chart_type": "bar",
      "total_sales": 960000,
      "max_value": 220000,
      "min_value": 55000,
      "avg_value": 137142.86,
      "total_products": 7,
      "top_3_products": [
        {"name": "Product 1089", "sales": 220000},
        {"name": "Product 1048", "sales": 180000},
        {"name": "Product 1024", "sales": 175000}
      ],
      "bottom_3_products": [
        {"name": "Product 1078", "sales": 120000},
        {"name": "Product 1041", "sales": 60000},
        {"name": "Product 1043", "sales": 55000}
      ],
      "concentration_ratio": 0.75,
      "performance_gap": 4.0,
      "trend": "upward",
      "pareto_effect": false
    },
    "raw_data": {
      "data_points": [
        ["Product 1089", 220000],
        ["Product 1048", 180000],
        ["Product 1024", 175000],
        ["Product 1003", 150000],
        ["Product 1078", 120000],
        ["Product 1041", 60000],
        ["Product 1043", 55000]
      ],
      "total_data_points": 7,
      "x_axis_label": "Product Category",
      "y_axis_label": "Sales Value (₱)"
    }
  }
]
```

---

## 4. Complete OpenAI Prompt

This is the EXACT prompt sent to OpenAI:

### System Message:
```
You are a senior business consultant and analytics expert for TANAW, an SME analytics platform.
```

### User Message:
```
You are a senior business consultant and analytics expert for TANAW, an SME analytics platform. Analyze each chart using the provided detailed data and generate intelligent, actionable business insights with specific recommendations.

For each chart, provide:

1. **BUSINESS DESCRIPTION**: What the chart reveals about business performance with specific data points
2. **STRATEGIC INSIGHT**: Key business implications and what this means for the organization
3. **ACTIONABLE RECOMMENDATIONS**: Specific, implementable strategies with timelines and expected outcomes
4. **RISK ASSESSMENT**: Potential risks or opportunities identified
5. **SUCCESS METRICS**: How to measure the impact of recommended actions

Chart-Specific Analysis Guidelines:

**SALES CHARTS:**
- Product Performance: Identify top/bottom performers, market concentration, pricing strategies
- Regional Sales: Geographic performance, market expansion opportunities, resource allocation
- Sales Trends: Growth patterns, seasonality, forecasting accuracy
- Sales Forecast: Future revenue projections, capacity planning, goal setting

**INVENTORY CHARTS:**
- Stock Levels: Inventory optimization, reorder points, storage costs
- Turnover Analysis: Cash flow implications, dead stock identification, supplier relationships
- Reorder Status: Supply chain efficiency, stockout prevention, cost optimization
- Stock Forecast: Demand planning, procurement strategies, working capital management

**FINANCE CHARTS:**
- Revenue Analysis: Income diversification, pricing optimization, market penetration
- Expense Distribution: Cost control opportunities, budget allocation, efficiency improvements
- Profit Margins: Pricing strategies, cost reduction, profitability enhancement
- Cash Flow: Working capital management, investment opportunities, financial planning

Requirements:
- Use EXACT data points, names, and values from the dataset
- Calculate specific percentages and ratios
- Provide concrete, implementable recommendations
- Include timelines (immediate, short-term, long-term)
- Reference specific products, regions, or metrics
- Consider SME context and resource constraints
- Focus on actionable insights that drive business growth

Return ONLY JSON in this exact format:
[
  {
    "chart_id": "...",
    "business_description": "Specific analysis of what the chart shows with actual data points",
    "strategic_insight": "Key business implications and organizational impact",
    "actionable_recommendations": [
      "Immediate action (0-30 days): Specific recommendation with expected outcome",
      "Short-term strategy (1-3 months): Detailed plan with success metrics",
      "Long-term opportunity (3-12 months): Strategic initiative with ROI projection"
    ],
    "risk_assessment": "Potential risks or opportunities identified",
    "success_metrics": "How to measure the impact of recommendations",
    "confidence": 0.0-1.0
  }
]

Charts:
[{"chart_id":"product_comparison_analysis","title":"Product Comparison by Sales","type":"bar","metrics":{"chart_type":"bar","total_sales":960000,"max_value":220000,"min_value":55000,"avg_value":137142.86,"total_products":7,"top_3_products":[{"name":"Product 1089","sales":220000},{"name":"Product 1048","sales":180000},{"name":"Product 1024","sales":175000}],"bottom_3_products":[{"name":"Product 1078","sales":120000},{"name":"Product 1041","sales":60000},{"name":"Product 1043","sales":55000}],"concentration_ratio":0.75,"performance_gap":4.0,"trend":"upward","pareto_effect":false},"raw_data":{"data_points":[["Product 1089",220000],["Product 1048",180000],["Product 1024",175000],["Product 1003",150000],["Product 1078",120000],["Product 1041",60000],["Product 1043",55000]],"total_data_points":7,"x_axis_label":"Product Category","y_axis_label":"Sales Value (₱)"}}]
```

---

## 5. OpenAI Response (Example)

This is what OpenAI returns to us:

```json
[
  {
    "chart_id": "product_comparison_analysis",
    "business_description": "The Product Comparison by Sales reveals significant performance disparities across your product portfolio. Product 1089 leads with ₱220,000 in sales (22.9% of total revenue), followed by Product 1048 at ₱180,000 (18.8%) and Product 1024 at ₱175,000 (18.2%). The top 3 products collectively account for 59.9% of total sales (₱575,000 out of ₱960,000), indicating strong concentration. However, the bottom performers (Products 1041 and 1043) generate only ₱115,000 combined (12% of total), with a 4x performance gap between the best and worst sellers.",
    
    "strategic_insight": "This sales distribution pattern suggests a concentrated revenue model with heavy reliance on a few star products. The 75% concentration ratio and clear performance stratification indicate both opportunity and risk: while top products drive substantial revenue, underperforming items may be tying up resources. The upward trend suggests growth momentum, but the wide performance gap reveals potential for portfolio optimization and resource reallocation.",
    
    "actionable_recommendations": [
      "Immediate action (0-30 days): Increase inventory and marketing budget for Products 1089, 1048, and 1024 by 15-20% to capitalize on their strong performance. Expected outcome: 10-15% revenue increase from top performers within the first month.",
      
      "Short-term strategy (1-3 months): Conduct customer surveys and market analysis for Products 1041 and 1043 to identify reasons for underperformance. Test promotional campaigns or bundling strategies. If no improvement, consider discontinuation to free up capital. Success metric: Increase bottom-tier sales by 30% or achieve cost savings of ₱50,000 through inventory reduction.",
      
      "Long-term opportunity (3-12 months): Develop 2-3 new products inspired by the attributes of top performers. Implement a product lifecycle management system to identify declining products earlier. ROI projection: Launch new products targeting ₱150,000-200,000 in sales each, potentially adding ₱300,000-400,000 to annual revenue."
    ],
    
    "risk_assessment": "Key risks include over-dependence on top 3 products (59.9% of revenue) which creates vulnerability to market changes, competition, or supply chain issues. The underperforming products (1041, 1043) represent potential dead stock and tied-up capital. Opportunities exist in understanding what makes the top products successful and replicating those factors, while also diversifying the product mix to reduce concentration risk.",
    
    "success_metrics": "Track monthly sales growth rate for top 3 products (target: +10-15%), measure inventory turnover ratio for bottom products (target: improvement from current level), monitor portfolio concentration ratio (target: reduce from 75% to 65% within 6 months by growing mid-tier products), and calculate ROI on marketing spend for each product category (target: 3:1 or better).",
    
    "confidence": 0.85
  }
]
```

---

## 6. How We Use the Response

After receiving this from OpenAI, we structure it for the frontend:

```json
{
  "chart_title": "Product Comparison by Sales",
  "domain": "sales",
  "business_description": "The Product Comparison by Sales reveals significant performance disparities...",
  "strategic_insight": "This sales distribution pattern suggests a concentrated revenue model...",
  "actionable_recommendations": [
    "Immediate action (0-30 days): Increase inventory and marketing budget...",
    "Short-term strategy (1-3 months): Conduct customer surveys...",
    "Long-term opportunity (3-12 months): Develop 2-3 new products..."
  ],
  "risk_assessment": "Key risks include over-dependence on top 3 products...",
  "success_metrics": "Track monthly sales growth rate for top 3 products...",
  "insights": "Combined text for backward compatibility",
  "key_points": ["Top 3 recommendations"],
  "confidence": 0.85,
  "generated_at": "2025-10-22T10:30:45.123456",
  "insight_type": "enhanced_business_recommendations"
}
```

---

## 7. Key Points

### What We Send to OpenAI:
1. ✅ **Chart metadata** (title, type, description)
2. ✅ **Calculated metrics** (totals, averages, trends)
3. ✅ **Top/Bottom performers** (specific names and values)
4. ✅ **Business ratios** (concentration, performance gap, Pareto effect)
5. ✅ **Raw data points** (limited to top 10 for token efficiency)

### What We DON'T Send:
1. ❌ **Full raw dataset** (too large, expensive)
2. ❌ **Chart images** (not needed, using data instead)
3. ❌ **User information** (privacy protection)
4. ❌ **Complete historical data** (filtered to relevant points)

### Why This Approach:
- **Cost-Effective**: Send only necessary data, reduce tokens
- **Intelligent**: Pre-calculated metrics help OpenAI focus on insights
- **Accurate**: Real product names and values for specific recommendations
- **Actionable**: Structured format ensures consistent, useful output
- **Fast**: Batch processing of 3 charts at a time
- **Reliable**: Fallback mechanisms if OpenAI fails

---

## 8. Token Usage

**Typical Request:**
- System Message: ~50 tokens
- User Prompt (Instructions): ~800 tokens
- Chart Data (per chart): ~300-500 tokens
- **Total per batch (3 charts)**: ~1,800-2,300 tokens

**Typical Response:**
- Per chart: ~400-600 tokens
- **Total per batch**: ~1,200-1,800 tokens

**Cost Estimate (GPT-4o-mini):**
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens
- **Per batch**: ~$0.001-0.002 (very cost-effective!)

---

## 9. Batch Processing

We process charts in batches of 3 to optimize:
- **API efficiency** (fewer calls)
- **Cost reduction** (batch discounts)
- **Speed** (parallel processing)
- **Rate limits** (avoid throttling)

Example batch:
```json
[
  {"chart_id": "product_performance", ...},
  {"chart_id": "sales_over_time", ...},
  {"chart_id": "stock_levels", ...}
]
```

All three get analyzed together in one API call!

---

## Summary

TANAW sends **highly structured, pre-processed data** to OpenAI with:
- Calculated business metrics
- Top/bottom performers
- Specific product names and values
- Clear instructions for SME-focused recommendations
- Structured output format

This ensures we get **accurate, actionable, cost-effective insights** that actually help business owners make decisions! 🎯✨

