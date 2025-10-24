# 🧪 TANAW Ambiguity Challenge - Test Files Guide

## 📋 Overview
These test files are designed to challenge TANAW's AI-powered column mapping and context detection capabilities. Each file contains intentionally ambiguous column names to test how well OpenAI can interpret semantic meaning.

---

## 📁 Test File 1: `ambiguous_test_challenge.csv`

### **Difficulty Level:** ⭐⭐⭐ Medium-High

### **What Makes It Challenging:**
1. **Multiple Date Columns** - `Date1` and `Date2` (which one is the transaction date?)
2. **Generic Numeric Columns** - `Value`, `Amount`, `Total`, `Balance`, `Rate` (which is sales?)
3. **Multiple Quantity Columns** - `Count`, `Qty`, `Units`, `Number` (which is the quantity sold?)
4. **Ambiguous Names** - `Name` (is it product? customer? or category?)
5. **Multiple Location Columns** - `Location1`, `Location2` (which is the sales region?)
6. **Multiple Price Columns** - `Price1`, `Price2` (which is the actual unit price?)
7. **Mixed Identifiers** - `ID`, `Code`, `Number` (which is the primary identifier?)

### **Expected TANAW Behavior:**
- Should map `Date1` → `Date` (primary date)
- Should map `Name` → `Product` (most likely entity identifier)
- Should map `Value` or `Amount` → `Sales` (prioritize primary monetary value)
- Should map `Location1` → `Region` (primary location)
- Should map `Qty` or `Count` → `Quantity` (primary count)
- Should mark duplicates as "Ignore"

### **Context Detection:**
- Ambiguous - could be SALES or INVENTORY or MIXED
- TANAW should analyze data patterns to determine

---

## 📁 Test File 2: `extreme_ambiguity_test.csv`

### **Difficulty Level:** ⭐⭐⭐⭐⭐ Extreme

### **What Makes It Challenging:**
1. **Ultra-Generic Column Names:**
   - `Time`, `Thing`, `Number`, `Value`, `Item`, `Data`, `Info`, `Code`, `Label`, `Metric`
2. **Single-Letter Column Names:**
   - `X`, `Y`, `Z`, `A`, `B`, `C`, `D` (completely meaningless!)
3. **Numbered Fields:**
   - `Field1`, `Field2`, `Field3` (no semantic meaning)
4. **No Clear Patterns:**
   - Almost impossible to determine without data analysis

### **Expected TANAW Behavior:**
- Should rely heavily on **data analysis** rather than column names
- Should examine sample values to infer meaning:
  - `Time` → `Date` (date values)
  - `Thing` → `Product` (looks like product names)
  - `Value` → `Sales` (monetary amounts)
  - `Data` → `Region` (location names like North, South)
- May use rule-based fallback for very ambiguous columns
- Should mark single-letter columns as "Ignore"

### **Context Detection:**
- Very difficult - requires data value analysis
- TANAW should send sample data to OpenAI for context detection

---

## 📁 Test File 3: `mixed_domain_confusion.csv`

### **Difficulty Level:** ⭐⭐⭐⭐ High

### **What Makes It Challenging:**
1. **Multi-Domain Dataset:**
   - SALES columns: `Sales`, `Transaction_Value`, `Amount_Paid`
   - INVENTORY columns: `Stock`, `Stock_Available`, `Reorder`, `Warehouse`, `Turnover`
   - FINANCE columns: `Revenue`, `Expense`, `Balance_Due`, `Unit_Cost`
   - CUSTOMER columns: `Customer_ID`, `Segment`, `Churn_Risk`

2. **Overlapping Semantics:**
   - `Sales` vs `Revenue` (both monetary, which to use?)
   - `Stock` vs `Stock_Available` (both inventory-related)
   - `Quantity_Sold` vs `Quantity` (redundant)
   - `Product_Code` vs `Product` (identifier confusion)

3. **Domain Confusion:**
   - Is this sales data? Inventory data? Finance? Customer analytics?
   - Answer: **MIXED DOMAIN** - all of the above!

### **Expected TANAW Behavior:**
- Should detect **MIXED** context
- Should prioritize primary columns:
  - `Entry_Date` → `Date`
  - `Sales` or `Revenue` → `Sales` (choose one, mark other as Ignore)
  - `Product_Code` → `Product`
  - `Warehouse` or `Location` → `Region`
  - `Quantity_Sold` → `Quantity`
- Should generate charts from multiple domains
- Should provide insights covering all business areas

### **Context Detection:**
- Should detect MIXED domain
- Should generate both SALES and INVENTORY charts

---

## 📁 Test File 4: `ultimate_ambiguity_challenge.csv`

### **Difficulty Level:** ⭐⭐⭐⭐⭐ Ultimate Challenge

### **What Makes It Challenging:**
1. **Duplicate Semantics:**
   - `date` vs `date_created` (which is transaction date?)
   - `name` vs `item` (both could be product or customer)
   - `value`, `amount`, `total`, `revenue`, `sales` (5 monetary columns!)
   - `cost` vs `expense` (both cost-related)
   - `price` (unit price or total?)
   - `quantity`, `count`, `stock`, `inventory` (4 quantity columns!)
   - `region`, `location`, `area`, `zone` (4 location columns!)

2. **Maximum Ambiguity:**
   - 20 columns with overlapping meanings
   - Multiple candidates for EVERY canonical type
   - Intentionally designed to confuse

3. **Mixed Interpretations:**
   - `name` could be customer name OR product name
   - `date_created` could be customer signup OR product added OR transaction date
   - `value` could be sales amount OR stock value OR customer lifetime value

### **Expected TANAW Behavior:**
- **Critical Test of AI Intelligence:**
  - Must analyze both column names AND data values
  - Must prioritize based on business logic
  - Must avoid duplicates

- **Expected Mappings:**
  - `date` → `Date` (shorter, more common for transaction date)
  - `item` → `Product` (more specific than "name")
  - `sales` → `Sales` (most explicit sales column)
  - `region` → `Region` (most standard location term)
  - `quantity` → `Quantity` (most standard count term)
  
- **Columns to Ignore:**
  - `date_created`, `name`, `value`, `amount`, `total`, `revenue`
  - `cost`, `expense`, `price`
  - `count`, `stock`, `inventory`
  - `location`, `area`, `zone`

### **Context Detection:**
- Extremely challenging
- Could be interpreted as SALES or INVENTORY or MIXED
- Should rely on data value analysis

---

## 🎯 Testing Strategy

### **For Each Test File:**

1. **Upload to TANAW**
2. **Observe Column Mapping:**
   - Which columns were mapped?
   - Which were marked as "Ignore"?
   - Are mappings correct?
   - Any duplicates?

3. **Check Context Detection:**
   - Did TANAW correctly identify domain (SALES/INVENTORY/FINANCE/CUSTOMER/MIXED)?
   - Was confidence level appropriate?
   - Was reasoning logical?

4. **Verify Chart Generation:**
   - Were appropriate charts generated?
   - Did charts use correct columns?
   - Were insights relevant?

5. **Test AI Robustness:**
   - Did system fall back to rules if OpenAI failed?
   - Were errors handled gracefully?
   - Did cache work correctly on re-upload?

---

## ✅ Success Criteria

### **Test File 1 (Medium-High):**
- ✅ Should correctly identify primary date, sales, product columns
- ✅ Should mark duplicate columns as "Ignore"
- ✅ Should detect SALES or MIXED context
- ✅ Should generate 3-5 relevant charts

### **Test File 2 (Extreme):**
- ✅ Should analyze data values to infer meaning
- ✅ Should handle generic column names
- ✅ Should mark meaningless columns (X, Y, Z) as "Ignore"
- ✅ Should detect context from data patterns

### **Test File 3 (High):**
- ✅ Should detect MIXED domain
- ✅ Should avoid mapping duplicates (Sales vs Revenue)
- ✅ Should generate charts from multiple domains
- ✅ Should provide comprehensive insights

### **Test File 4 (Ultimate):**
- ✅ Should demonstrate advanced AI reasoning
- ✅ Should prioritize correct columns from 20 options
- ✅ Should avoid ALL duplicates
- ✅ Should generate accurate, non-misleading charts
- ✅ Should provide confidence scores appropriately

---

## 🔍 Key Questions to Answer

1. **Column Mapping Accuracy:**
   - Did OpenAI choose the correct primary columns?
   - Were duplicates properly handled?
   - Were confidence scores appropriate?

2. **Context Detection:**
   - Did semantic detector correctly identify domain?
   - Was reasoning logical?
   - Did it handle mixed domains?

3. **Fallback Systems:**
   - Did rule-based fallback work when needed?
   - Were fallback mappings reasonable?
   - Was system robust to OpenAI failures?

4. **Cost Efficiency:**
   - How many columns were cached?
   - What was total OpenAI cost?
   - Was caching effective?

5. **Chart Quality:**
   - Were generated charts meaningful?
   - Did charts use correct data?
   - Were insights actionable?

---

## 💡 Expected AI Behavior

### **OpenAI Should:**
1. ✅ Analyze semantic meaning, not just keywords
2. ✅ Prioritize explicit terms over generic ones
3. ✅ Choose ONE column per canonical type (avoid duplicates)
4. ✅ Mark ambiguous/secondary columns as "Ignore"
5. ✅ Provide logical reasoning for decisions
6. ✅ Give appropriate confidence scores
7. ✅ Handle edge cases gracefully

### **TANAW Should:**
1. ✅ Use cache for repeated column names
2. ✅ Fall back to rules if OpenAI fails
3. ✅ Validate mappings before processing
4. ✅ Detect mixed domains correctly
5. ✅ Generate relevant charts only
6. ✅ Provide actionable insights
7. ✅ Handle errors gracefully

---

## 🚀 How to Run Tests

1. **Navigate to TANAW Dashboard**
2. **Upload each test file one by one**
3. **Observe the mapping process:**
   - Check console logs for OpenAI responses
   - Note which columns were cached
   - Review confidence scores

4. **Analyze Results:**
   - Review column mappings
   - Check context detection
   - Examine generated charts
   - Read narrative insights

5. **Test Re-Upload:**
   - Upload same file again
   - Verify cache hits increase
   - Confirm consistent mappings

---

## 📊 Expected Results Summary

| Test File | Difficulty | Expected Context | Key Challenge | Success Metric |
|-----------|-----------|------------------|---------------|----------------|
| ambiguous_test_challenge.csv | ⭐⭐⭐ | SALES/MIXED | Multiple similar columns | Correct primary column selection |
| extreme_ambiguity_test.csv | ⭐⭐⭐⭐⭐ | UNKNOWN → SALES | Generic/meaningless names | Data-driven inference |
| mixed_domain_confusion.csv | ⭐⭐⭐⭐ | MIXED | Multi-domain overlap | Handle all domains correctly |
| ultimate_ambiguity_challenge.csv | ⭐⭐⭐⭐⭐ | SALES/MIXED | Maximum duplication | Perfect prioritization |

---

## 🎓 Learning Objectives

These test files help verify:
1. **OpenAI's semantic understanding** vs simple keyword matching
2. **TANAW's ability to handle ambiguity** in real-world data
3. **Robustness** of the 3-layer fallback system
4. **Cost efficiency** through caching
5. **Context detection accuracy** across domains
6. **Chart generation quality** with ambiguous data

---

**Good luck testing! These files will truly challenge TANAW's AI capabilities!** 🚀✨

*Note: These are intentionally difficult test cases. Real-world datasets are usually less ambiguous. If TANAW handles these well, it can handle almost any business dataset!*

