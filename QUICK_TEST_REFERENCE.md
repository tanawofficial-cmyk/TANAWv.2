# 🚀 Quick Test Reference - Finance Chart 1

## Test File
📁 **Location**: `TEST FILES/finance_test_revenue_expense.csv`

## What to Expect

### Chart Details
- 📊 **Title**: "Revenue and Expense Trend"
- 🎨 **Icon**: 💰
- 📈 **Type**: Multi-Series Line Chart
- 🎨 **Lines**: 
  - Green line = Revenue (₱15K - ₱31K)
  - Red line = Expenses (₱11K - ₱24K)

### Key Numbers (from test data)
- 📊 **Total Revenue**: ₱689,500
- 💰 **Total Expenses**: ₱512,000
- 💵 **Net Profit**: ₱177,500
- 📈 **Profit Margin**: 25.74%
- ✅ **Profitable Days**: 30/30 (100%)

## Quick Validation

### ✅ SUCCESS if you see:
1. Chart titled "Revenue and Expense Trend" with 💰 icon
2. TWO lines on the same chart (green + red)
3. Green line above red line (revenue > expenses)
4. X-axis shows dates (Jan 1 - Jan 30, 2024)
5. Y-axis shows amounts in pesos (₱)
6. Tooltip shows both Revenue and Expenses when hovering
7. NO duplicate line charts with same data

### ❌ FAIL if you see:
1. Chart missing or not displayed
2. Only ONE line showing
3. Duplicate chart with same data but different title
4. Error messages in console
5. Chart shows wrong data (not matching CSV values)

## First Data Point Verification
Hover over **January 1, 2024**:
- Should show: **Revenue: ₱15,000** and **Expenses: ₱12,000**

## Last Data Point Verification
Hover over **January 30, 2024**:
- Should show: **Revenue: ₱25,000** and **Expenses: ₱19,500**

## Flask Log Check
Search logs for:
```
✅ Successfully generated Revenue and Expense Trend
✅ Added 1 Finance charts
```

## Browser DevTools Check
1. Open DevTools (F12)
2. Network tab → Find `/api/files/upload-clean` request
3. Check Response → Look for:
```json
{
  "id": "revenue_expense_trend",
  "domain": "finance",
  "data": {
    "series": [
      {"name": "Revenue", "color": "#10b981"},
      {"name": "Expenses", "color": "#ef4444"}
    ]
  }
}
```

## 🎯 Test Now!
1. Upload the CSV file
2. Wait for processing
3. Check for the chart
4. Report back with results! 🚀

