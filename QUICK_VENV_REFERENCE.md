# 🚀 Quick Virtual Environment Reference

**ONE VENV TO RULE THEM ALL**

---

## ✅ The ONLY Virtual Environment to Use

```
Location: D:\Documents-BatState-U\CAPSTONE PROJECT\TANAW\venv_tanaw312
Python:   3.12.10
Packages: 114 (complete with all dependencies)
```

---

## ⚡ Quick Commands

### Activate Virtual Environment
```powershell
cd "D:\Documents-BatState-U\CAPSTONE PROJECT\TANAW"
.\venv_tanaw312\Scripts\Activate.ps1
```

### Run Backend (Node.js)
```powershell
cd backend
npm start
```

### Run Analytics Service (Python)
```powershell
# Make sure venv is activated first!
.\venv_tanaw312\Scripts\Activate.ps1

cd backend\analytics_service
python app_clean.py
```

### Run Frontend (React)
```powershell
cd frontend
npm start
```

### Install New Python Package
```powershell
.\venv_tanaw312\Scripts\Activate.ps1
pip install package-name

# Update requirements
pip freeze > backend\analytics_service\requirements.txt
```

---

## ❌ DO NOT USE

~~`backend\analytics_service\venv`~~ ← **INCOMPLETE - DO NOT USE**

This venv only has 21 packages and is missing:
- ❌ openai
- ❌ pymongo
- ❌ prophet
- ❌ statsmodels
- ❌ torch/transformers

**Using it will cause import errors!**

To remove it:
```powershell
.\cleanup_venv.ps1
```

---

## 🔍 Verify Your Setup

```powershell
# Activate venv
.\venv_tanaw312\Scripts\Activate.ps1

# Check Python version
python --version
# Should show: Python 3.12.10

# Check critical packages
python -m pip show openai pymongo prophet flask pandas

# All should show "Name: <package>" and "Version: <version>"
```

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'openai'"

**Problem:** You're not using the correct venv

**Solution:**
```powershell
# Deactivate any active venv
deactivate

# Activate the correct one
cd "D:\Documents-BatState-U\CAPSTONE PROJECT\TANAW"
.\venv_tanaw312\Scripts\Activate.ps1

# Verify
python -m pip show openai
```

### "Cannot activate venv_tanaw312"

**Problem:** Execution policy restrictions

**Solution:**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
.\venv_tanaw312\Scripts\Activate.ps1
```

### "Wrong Python version"

**Problem:** System Python being used instead of venv

**Solution:**
```powershell
# Make sure venv is activated (prompt should show (venv_tanaw312))
.\venv_tanaw312\Scripts\Activate.ps1

# Use absolute path to Python
.\venv_tanaw312\Scripts\python.exe your_script.py
```

---

## 📋 Package Inventory

**Complete list of installed packages in venv_tanaw312:**

### Core Python & Data Science
- pandas 2.3.3
- numpy 2.3.3
- scipy 1.16.2
- scikit-learn 1.7.2

### Web Framework
- Flask 3.1.2
- flask-cors 6.0.1

### AI & Machine Learning
- openai 2.3.0
- torch 2.8.0
- transformers 4.57.0
- sentence-transformers 5.1.1

### Time Series & Forecasting
- prophet 1.1.7
- statsmodels 0.14.5

### Database
- pymongo 4.15.3
- SQLAlchemy 2.0.43

### Visualization
- matplotlib 3.10.7
- seaborn 0.13.2
- plotly 6.3.1

### Data Quality & Validation
- great_expectations 1.7.0
- pandera 0.26.1

### Development Tools
- pytest 8.4.2
- pytest-cov 7.0.0
- black 25.9.0
- flake8 7.3.0

**Total: 114 packages** ✅

---

## 📚 Related Documentation

- **Full Analysis:** `VENV_CONSOLIDATION_REPORT.md`
- **Cleanup Script:** `cleanup_venv.ps1`
- **OpenAI Setup:** `backend/analytics_service/OPENAI_SETUP_COMPLETE_GUIDE.md`
- **Deployment:** `TANAW_TECH_STACK_AND_DEPLOYMENT.md`

---

**Last Updated:** October 24, 2025

