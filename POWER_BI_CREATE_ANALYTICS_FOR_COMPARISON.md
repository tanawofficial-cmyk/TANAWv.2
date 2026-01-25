# Create Power BI Analytics for TANAW Comparison

This guide shows you how to create the **exact same analytics** in Power BI that TANAW generates, so you can compare and prove TANAW's reliability.

---

## Part 1: Create Top 5 Products Chart (Coffee Dataset)

### Step 1: Load Coffee Data
1. **Get Data** → **Text/CSV**
2. Select `coffee.csv`
3. Click **Load**

### Step 2: Create Bar Chart
1. Click **Stacked Bar Chart** icon
2. Drag `coffee_name` to **Y-axis**
3. Drag `money` to **X-axis** (it will show as "Sum of money")

### Step 3: Sort and Filter to Top 5
1. Click **Sort** icon → Sort by "Sum of money" → **Descending**
2. In **Filters** pane:
   - Find `coffee_name` filter
   - Click dropdown → Select **Top N**
   - Set: **Top 5** by "Sum of money"
   - Click **Apply filter**

### Step 4: Get Exact Values
**Method A: Hover over bars**
- Hover over each bar to see tooltip with exact value
- Record: Latte = ?, Americano with Milk = ?, etc.

**Method B: Create Table (More Accurate)**
1. Click **Table** icon in Visualizations pane
2. **EASIEST:** Look at LEFT SIDE (Fields list) and check boxes:
   - ☑ Check `coffee_name`
   - ☑ Check `money`
3. Table will automatically show `coffee_name` and `Sum of money` columns
4. **Sort:**
   - Click dropdown arrow (▼) next to "Sum of money" column header
   - Select **Sort descending**
5. You'll see exact values in the table, sorted from highest to lowest
6. Record top 5 values

### Step 5: Record Values for Comparison
Fill these in your comparison table:
- Latte: [Your Power BI value]
- Americano with Milk: [Your Power BI value]
- Cappuccino: [Your Power BI value]
- Americano: [Your Power BI value]
- Hot Chocolate: [Your Power BI value]

**Expected TANAW Values:**
- Latte: PHP 27,866.30
- Americano with Milk: PHP 25,269.12
- Cappuccino: PHP 18,034.14
- Americano: PHP 15,062.26
- Hot Chocolate: PHP 10,172.46

---

## Part 2: Create Sales Over Time Chart (Coffee Dataset)

### Step 1: Create Line Chart
1. Click **Line Chart** icon
2. Drag `date` to **X-axis**
3. Drag `money` to **Y-axis** (it will show as "Sum of money")

### Step 2: Set to Daily Granularity
1. In **Visualizations** pane, find **X-axis** section
2. Click dropdown arrow (▼) next to `date`
3. Select **`date` (Day)** from the list
4. Verify: Chart should show 381 data points

### Step 3: Get Total Sales
1. Right-click `coffee` table → **New measure**
2. Formula:
   ```
   Total Sales Coffee = SUM(coffee[money])
   ```
3. Create **Card** visual
4. Drag `Total Sales Coffee` measure to it
5. Record value: [Your Power BI value]

**Expected TANAW Value:** PHP 115,431.58

### Step 4: Get Total Days
1. Right-click `coffee` table → **New measure**
2. Formula:
   ```
   Total Days Coffee = DISTINCTCOUNT(coffee[date])
   ```
3. Create **Card** visual
4. Drag `Total Days Coffee` measure to it
5. Record value: [Your Power BI value]

**Expected TANAW Value:** 381 days

### Step 5: Get Peak Performance Dates

**EASIEST METHOD (Using Checkboxes):**

1. Click **Table** icon in Visualizations pane (grid icon on the right side)
2. An empty table will appear on your canvas
3. **Look at the LEFT SIDE** - You'll see the **Fields** list (all your columns)
4. **Simply check the boxes:**
   - ☑ Click checkbox next to `date`
   - ☑ Click checkbox next to `money`
5. **That's it!** The table will automatically show:
   - Column 1: `date`
   - Column 2: `Sum of money`

**ALTERNATIVE METHOD (If checkboxes don't work):**

1. Click **Table** icon
2. Empty table appears on canvas
3. **Look at the RIGHT SIDE** - Visualizations pane
4. Scroll down to find **"Fields"** section or **"Values"** section
5. **Drag fields:**
   - From LEFT side (Fields list), drag `date` 
   - Drop it into the **Values** section (right side) OR directly onto the empty table
   - From LEFT side, drag `money`
   - Drop it into **Values** section OR onto the table

**Sort the Table to Find Peak Dates:**

1. **For Peak Date (Highest Sale):**
   - Click the dropdown arrow (▼) next to "Sum of money" column header
   - Select **Sort descending** → Top row shows peak date & amount
   - Record: Peak Date = [top row date], Peak Amount = [top row amount]

2. **For Lowest Date (Lowest Sale):**
   - Click dropdown arrow (▼) next to "Sum of money" column header again
   - Select **Sort ascending** → Top row shows lowest date & amount
   - Record: Lowest Date = [top row date], Lowest Amount = [top row amount]

**Expected TANAW Values:**
- Peak Date: 2024-10-11
- Peak Amount: PHP 836.66
- Lowest Date: 2024-08-29
- Lowest Amount: PHP 23.02

### Step 6: Get Average Daily Sales
1. Right-click `coffee` table → **New measure**
2. Formula:
   ```
   Avg Daily Sales = AVERAGEX(VALUES(coffee[date]), CALCULATE(SUM(coffee[money])))
   ```
3. Create **Card** visual
4. Drag `Avg Daily Sales` measure to it
5. Record value: [Your Power BI value]

**Expected TANAW Value:** PHP 302.97

---

## Part 3: Create Top 5 Products Chart (Fashion Dataset)

### Step 1: Load Fashion Data
1. **Get Data** → **Text/CSV**
2. Select `Fashion_Retail_Sales.csv`
3. Click **Load**

### Step 2: Create Bar Chart
1. Click **Stacked Bar Chart** icon
2. Drag `Item Purchased` to **Y-axis**
3. Drag `Purchase Amount (USD)` to **X-axis**

### Step 3: Sort and Filter to Top 5
1. Sort by "Sum of Purchase Amount (USD)" → **Descending**
2. Filter: **Top 5** by "Sum of Purchase Amount (USD)"

### Step 4: Get Exact Values
1. Create **Table** visual
2. Drag `Item Purchased` to **Rows**
3. Drag `Purchase Amount (USD)` (Sum) to **Values**
4. Sort descending
5. Record top 5 values

**Expected TANAW Values:**
- Tunic: USD 17,275.00
- Jeans: USD 13,068.00
- Pajamas: USD 12,798.00
- Shorts: USD 12,702.00
- Handbag: USD 12,668.00

---

## Part 4: Create Sales Over Time Chart (Fashion Dataset)

### Step 1: Create Line Chart
1. Click **Line Chart** icon
2. Drag `Date Purchase` to **X-axis**
3. Drag `Purchase Amount (USD)` to **Y-axis**

### Step 2: Set to Daily Granularity
1. Click dropdown (▼) next to `Date Purchase` in X-axis
2. Select **`Date Purchase` (Day)**
3. Verify: Chart should show 365 data points

### Step 3: Get Total Sales
1. Create measure:
   ```
   Total Sales Fashion = SUM(Fashion_Retail_Sales[Purchase Amount (USD)])
   ```
2. Create **Card** visual
3. Record value

**Expected TANAW Value:** USD 430,952.00

### Step 4: Get Total Days
1. Create measure:
   ```
   Total Days Fashion = DISTINCTCOUNT(Fashion_Retail_Sales[Date Purchase])
   ```
2. Create **Card** visual
3. Record value

**Expected TANAW Value:** 365 days

### Step 5: Get Peak Performance Dates
1. Create **Table** visual
2. Drag `Date Purchase` to **Rows**
3. Drag `Purchase Amount (USD)` (Sum) to **Values**
4. Sort descending → Top row = Peak
5. Sort ascending → Top row = Lowest
6. Record values

**Expected TANAW Values:**
- Peak Date: 2022-11-21
- Peak Amount: USD 9,481.00
- Lowest Date: 2023-02-12
- Lowest Amount: USD 118.00

---

## Part 5: Compare Values

### Create Comparison Table in Power BI

1. **Enter Data** → Create table:
   - Columns: `Metric`, `TANAW_Value`, `PowerBI_Value`, `Match`
   
2. Fill in values from your charts

3. Add calculated column:
   ```
   Match = IF([TANAW_Value] = [PowerBI_Value], "EXACT MATCH", "DIFFERENCE")
   ```

4. Create **Table** visual to show comparison

### Verify Accuracy

**Exact Match Criteria:**
- Product sales: Should match exactly (same calculation)
- Total sales: Should match exactly
- Total days: Should match exactly
- Peak dates: Should match exactly
- Peak amounts: Should match exactly

**If values match:** ✅ TANAW is reliable and accurate!

**If values differ:**
- Check for filters applied in Power BI
- Verify date range matches
- Check aggregation method (Sum vs Average)
- Verify data type handling

---

## Quick Reference: All Expected TANAW Values

### Coffee Dataset
- **Top 5 Products:** Latte (27,866.30), Americano with Milk (25,269.12), Cappuccino (18,034.14), Americano (15,062.26), Hot Chocolate (10,172.46)
- **Total Sales:** PHP 115,431.58
- **Total Days:** 381
- **Peak Date:** 2024-10-11
- **Peak Amount:** PHP 836.66
- **Lowest Date:** 2024-08-29
- **Lowest Amount:** PHP 23.02

### Fashion Dataset
- **Top 5 Products:** Tunic (17,275.00), Jeans (13,068.00), Pajamas (12,798.00), Shorts (12,702.00), Handbag (12,668.00)
- **Total Sales:** USD 430,952.00
- **Total Days:** 365
- **Peak Date:** 2022-11-21
- **Peak Amount:** USD 9,481.00
- **Lowest Date:** 2023-02-12
- **Lowest Amount:** USD 118.00

---

## Proving TANAW Reliability

After creating all charts in Power BI:

1. **Compare each value** with TANAW
2. **Document matches** - Shows TANAW is accurate
3. **Document differences** - Investigate why (filters, date ranges, etc.)
4. **Create summary** - "TANAW matches Power BI with X% accuracy"

This proves TANAW's reliability for your manuscript!

