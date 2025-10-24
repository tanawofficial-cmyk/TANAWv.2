# Narrative Insights Data Flow

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TANAW NARRATIVE INSIGHTS FLOW                    │
└─────────────────────────────────────────────────────────────────────────┘

Step 1: Chart Generation
┌──────────────────────────────────────────┐
│   Bar/Line/Forecast Chart Generators     │
│                                          │
│   Output:                                │
│   {                                      │
│     id: "product_comparison",            │
│     title: "Product Comparison by Sales",│
│     type: "bar",                         │
│     data: {                              │
│       x: ["Product A", "Product B"...],  │
│       y: [220000, 180000, ...]           │
│     }                                    │
│   }                                      │
└──────────────────────────────────────────┘
                    ↓
                    
Step 2: Metric Extraction (narrative_insights.py)
┌──────────────────────────────────────────┐
│   _extract_chart_summaries()             │
│   _extract_key_metrics()                 │
│                                          │
│   Calculates:                            │
│   ✓ Total sales: 960,000                 │
│   ✓ Average: 137,142                     │
│   ✓ Top 3 products with values           │
│   ✓ Bottom 3 products with values        │
│   ✓ Concentration ratio: 0.75            │
│   ✓ Performance gap: 4.0x                │
│   ✓ Trend analysis: "upward"             │
│   ✓ Pareto effect: false                 │
└──────────────────────────────────────────┘
                    ↓
                    
Step 3: Batch Preparation
┌──────────────────────────────────────────┐
│   _chunk_charts() - Group 3 charts       │
│                                          │
│   Batch = [Chart1, Chart2, Chart3]       │
│                                          │
│   Each chart includes:                   │
│   • Metadata (id, title, type)           │
│   • Calculated metrics                   │
│   • Raw data points (top 10)             │
│   • Axis labels                          │
└──────────────────────────────────────────┘
                    ↓
                    
Step 4: Prompt Generation
┌──────────────────────────────────────────┐
│   _create_batch_prompt()                 │
│                                          │
│   Creates comprehensive prompt with:     │
│   📋 System context                      │
│   📊 Chart-specific guidelines           │
│   💡 SME-focused requirements            │
│   📈 Expected JSON structure             │
│   🔢 Batch chart data                    │
└──────────────────────────────────────────┘
                    ↓
                    
Step 5: OpenAI API Call
┌──────────────────────────────────────────┐
│   OpenAI GPT-4o-mini                     │
│                                          │
│   Model: gpt-4o-mini                     │
│   Max Tokens: 300                        │
│   Temperature: 0.7                       │
│   Retries: 3 with exponential backoff    │
│                                          │
│   Cost: ~$0.001 per batch               │
└──────────────────────────────────────────┘
                    ↓
                    
Step 6: Response Parsing
┌──────────────────────────────────────────┐
│   _parse_batch_response()                │
│                                          │
│   Extracts:                              │
│   {                                      │
│     business_description: "...",         │
│     strategic_insight: "...",            │
│     actionable_recommendations: [        │
│       "Immediate (0-30 days): ...",      │
│       "Short-term (1-3 months): ...",    │
│       "Long-term (3-12 months): ..."     │
│     ],                                   │
│     risk_assessment: "...",              │
│     success_metrics: "...",              │
│     confidence: 0.85                     │
│   }                                      │
└──────────────────────────────────────────┘
                    ↓
                    
Step 7: Frontend Display
┌──────────────────────────────────────────┐
│   Dashboard.js - Enhanced UI             │
│                                          │
│   🧠 Business Intelligence               │
│   ├─ 📊 Business Analysis                │
│   ├─ 🎯 Strategic Insight                │
│   ├─ 🚀 Actionable Recommendations       │
│   ├─ ⚠️  Risk Assessment                 │
│   └─ 📈 Success Metrics                  │
│                                          │
│   Confidence: 85% ✅                     │
└──────────────────────────────────────────┘
```

---

## Data Sample: Real Example

### INPUT (What we calculate from chart):
```json
{
  "chart_id": "product_comparison_analysis",
  "title": "Product Comparison by Sales",
  "type": "bar",
  "metrics": {
    "total_sales": 960000,
    "avg_value": 137142.86,
    "top_3_products": [
      {"name": "Product 1089", "sales": 220000},
      {"name": "Product 1048", "sales": 180000},
      {"name": "Product 1024", "sales": 175000}
    ],
    "concentration_ratio": 0.75,
    "pareto_effect": false
  },
  "raw_data": {
    "data_points": [
      ["Product 1089", 220000],
      ["Product 1048", 180000],
      ["Product 1024", 175000]
    ]
  }
}
```

### PROMPT (What we ask OpenAI):
```
You are a senior business consultant. Analyze this chart:

Chart: Product Comparison by Sales
Metrics:
- Total Sales: ₱960,000
- Top Product: Product 1089 (₱220,000 - 22.9% of total)
- Top 3 Account For: 59.9% of revenue
- Performance Gap: 4.0x between best and worst

Provide:
1. Business Description (with specific data)
2. Strategic Insight (organizational impact)
3. Actionable Recommendations (3 items with timelines)
4. Risk Assessment
5. Success Metrics
```

### OUTPUT (What OpenAI returns):
```json
{
  "business_description": "Product 1089 leads with ₱220,000 (22.9% of revenue), followed by Product 1048 at ₱180,000 (18.8%). Top 3 products account for 59.9% of total sales, showing strong concentration.",
  
  "strategic_insight": "Heavy reliance on a few star products creates both opportunity and risk. The 75% concentration indicates potential for portfolio optimization.",
  
  "actionable_recommendations": [
    "Immediate (0-30 days): Increase inventory for top 3 products by 15-20%. Expected: 10-15% revenue boost.",
    "Short-term (1-3 months): Analyze underperformers, test promotions. Target: 30% sales increase or cost savings.",
    "Long-term (3-12 months): Develop new products inspired by top performers. ROI: ₱300,000-400,000 additional revenue."
  ],
  
  "risk_assessment": "Over-dependence on top 3 products (59.9%) creates vulnerability. Underperformers tie up capital.",
  
  "success_metrics": "Track top 3 growth rate (target: +10-15%), monitor concentration ratio (reduce to 65%), measure marketing ROI (target: 3:1).",
  
  "confidence": 0.85
}
```

---

## Key Features

### 🎯 Data Efficiency
- **Pre-calculated metrics** reduce OpenAI processing
- **Top 10 data points** only (not full dataset)
- **Structured format** for consistent results

### 💰 Cost Optimization
- **Batch processing** (3 charts per call)
- **GPT-4o-mini** (cost-effective model)
- **~$0.001 per batch** of 3 charts

### 🛡️ Error Handling
- **3 retry attempts** with exponential backoff
- **Fallback insights** if OpenAI fails
- **JSON parsing recovery** for malformed responses

### 📊 Business Focus
- **SME-specific** recommendations
- **Timeline-based** actions (immediate/short/long)
- **Measurable outcomes** and success metrics
- **Risk-aware** analysis

---

## Token Breakdown

### Per Chart Analysis:

```
Prompt (Input):
├─ System message: 50 tokens
├─ Instructions: 800 tokens
├─ Chart metadata: 100 tokens
├─ Metrics: 150 tokens
└─ Raw data: 100 tokens
Total Input: ~1,200 tokens per chart

Response (Output):
├─ Business description: 100 tokens
├─ Strategic insight: 80 tokens
├─ Recommendations (3x): 200 tokens
├─ Risk assessment: 80 tokens
└─ Success metrics: 80 tokens
Total Output: ~540 tokens per chart
```

### Batch of 3 Charts:
- **Input**: ~2,300 tokens
- **Output**: ~1,600 tokens
- **Cost**: ~$0.0015 USD

### For 10 Charts (Full Analysis):
- **4 batches** (3+3+3+1)
- **Total cost**: ~$0.005-0.008 USD
- **Processing time**: 8-12 seconds

**Extremely cost-effective for the value provided!** 💎

---

## Error Handling Flow

```
Try: OpenAI API Call
  ├─ Success → Parse Response → Return Insights
  │
  ├─ Failure (Attempt 1) → Wait 2s → Retry
  │   ├─ Success → Parse Response → Return Insights
  │   └─ Failure (Attempt 2) → Wait 4s → Retry
  │       ├─ Success → Parse Response → Return Insights
  │       └─ Failure (Attempt 3) → Wait 8s → Retry
  │           ├─ Success → Parse Response → Return Insights
  │           └─ Failure → Return Fallback Insights
  │
  └─ JSON Parse Error → Extract Valid Part → Return Insights
      └─ Complete Failure → Return Enhanced Fallback
```

**Fallback Insights** are high-quality, generic recommendations that still provide value even when OpenAI is unavailable.

---

## Summary

TANAW's narrative insights system is:
- 🎯 **Intelligent**: Pre-processes data for better insights
- 💰 **Cost-effective**: ~$0.001 per batch of 3 charts
- ⚡ **Fast**: Batch processing for speed
- 🛡️ **Reliable**: Multiple fallback mechanisms
- 📊 **Actionable**: SME-focused recommendations with timelines
- 🔒 **Private**: No sensitive data sent to OpenAI

This makes TANAW's AI insights both **powerful and practical** for small business owners! 🚀✨

