# ⚡ TANAW - 30-Minute Deployment Guide

## 🎯 **Goal: Deploy TANAW to FREE Cloud Hosting**

**Time:** 30 minutes  
**Cost:** $0/month (FREE tier)  
**Result:** Live, accessible system with professional URLs

---

## 📋 **Pre-Deployment Checklist**

- [ ] Code is working locally
- [ ] MongoDB Atlas is set up
- [ ] OpenAI API key obtained
- [ ] Email service configured (optional)
- [ ] All .env variables documented

---

## 🚀 **Quick Deployment (3 Services)**

### **Service 1: MongoDB Atlas** (Already Done ✅)
**Status:** ✅ Already configured
**URL:** `tanaw-cluster.ubmkkhg.mongodb.net`
**Time:** 0 minutes (skip)

---

### **Service 2: Deploy Backend API** (10 minutes)

**Platform:** Render.com (FREE)

#### **Steps:**

1. **Create Render Account**
   - Go to: https://render.com
   - Sign up with GitHub (free)

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Or use "Public Git Repository" if not on GitHub

3. **Configure Backend**
   ```
   Name: tanaw-backend
   Region: Oregon (or closest to you)
   Branch: main
   Root Directory: backend
   Runtime: Node
   Build Command: npm install
   Start Command: npm start
   Plan: Free
   ```

4. **Add Environment Variables**
   ```
   MONGO_URI = mongodb+srv://tanaw_admin:jelsonU150308@tanaw-cluster.ubmkkhg.mongodb.net/?retryWrites=true&w=majority&appName=tanaw-cluster
   JWT_SECRET = tanaw_secret_key_2025_capstone
   ADMIN_LICENSE_KEY = secretTANAWKey
   EMAIL_USER = your-email@gmail.com (optional)
   EMAIL_PASS = your-app-password (optional)
   PORT = 5000
   ANALYTICS_SERVICE_URL = (leave empty for now)
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes
   - Note the URL: `https://tanaw-backend.onrender.com`

**Test:** Visit `https://tanaw-backend.onrender.com/api/health`
Should return: `{"status": "healthy"}`

---

### **Service 3: Deploy Analytics Service** (10 minutes)

**Platform:** Render.com (FREE)

#### **Steps:**

1. **Create Another Web Service**
   - Click "New +" → "Web Service"
   - Same repository

2. **Configure Analytics**
   ```
   Name: tanaw-analytics
   Region: Oregon
   Branch: main
   Root Directory: backend/analytics_service
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python app_clean.py
   Plan: Free
   ```

3. **Add Environment Variables**
   ```
   OPENAI_API_KEY = sk-your-openai-key-here
   FLASK_ENV = production
   FLASK_PORT = 5001
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait 5-7 minutes (Python takes longer)
   - Note the URL: `https://tanaw-analytics.onrender.com`

**Test:** Visit `https://tanaw-analytics.onrender.com/api/health`

5. **Update Backend Environment**
   - Go back to tanaw-backend settings
   - Add: `ANALYTICS_SERVICE_URL = https://tanaw-analytics.onrender.com`
   - Redeploy backend

---

### **Service 4: Deploy Frontend** (5 minutes)

**Platform:** Netlify (FREE, unlimited bandwidth!)

#### **Steps:**

1. **Create Netlify Account**
   - Go to: https://www.netlify.com
   - Sign up with GitHub (free)

2. **Deploy via Drag & Drop** (Easiest)
   ```bash
   # Build frontend locally
   cd frontend
   npm install
   npm run build
   ```
   
   - Go to: https://app.netlify.com/drop
   - Drag `frontend/build` folder
   - Done! 🎉

3. **Or Deploy via CLI** (More professional)
   ```bash
   npm install -g netlify-cli
   cd frontend
   netlify deploy --prod
   ```

4. **Configure Environment**
   - Go to Site Settings → Environment Variables
   - Add: `REACT_APP_API_URL = https://tanaw-backend.onrender.com`
   - Redeploy

5. **Your Site is Live!**
   - URL: `https://your-site-name.netlify.app`
   - Or set custom domain

**Test:** Visit your Netlify URL, should see TANAW landing page

---

## ✅ **Deployment Complete!**

### **Your Live URLs:**
```
Frontend:  https://[your-site].netlify.app
Backend:   https://tanaw-backend.onrender.com
Analytics: https://tanaw-analytics.onrender.com
Database:  MongoDB Atlas (cloud)
```

### **Test the System:**
1. Visit frontend URL
2. Register an account
3. Login
4. Upload a test CSV
5. See AI-generated charts!

---

## ⚠️ **Important Notes**

### **Free Tier Limitations:**
- ⏰ **Auto-sleep:** Services sleep after 15 min inactivity
- ⏰ **Wake time:** ~30 seconds for first request
- 💾 **Storage:** Ephemeral (uploaded files deleted on restart)
- ⏱️ **Compute:** 750 hours/month limit

**For Defense:** Acceptable! Just wake services before demo.

### **Production Considerations:**
- 💰 Upgrade to paid tier ($7-19/month per service)
- 💾 Use AWS S3 for persistent file storage
- 📧 Configure email service properly
- 🔐 Add rate limiting
- 📊 Set up monitoring (optional)

---

## 🐛 **Troubleshooting**

### **Backend won't start:**
```
Check:
1. MONGO_URI is correct
2. All dependencies in package.json
3. Port 5000 not hardcoded
4. Look at Render logs
```

### **Analytics service won't start:**
```
Check:
1. OPENAI_API_KEY is set
2. requirements.txt has all packages
3. Python version is 3.12
4. Look at Render logs
```

### **Frontend can't connect to backend:**
```
Check:
1. REACT_APP_API_URL is correct
2. Backend CORS allows frontend domain
3. Backend is running (visit /api/health)
4. Rebuild frontend after env change
```

### **Charts not generating:**
```
Check:
1. Analytics service is running
2. ANALYTICS_SERVICE_URL in backend is correct
3. OPENAI_API_KEY is valid
4. Check analytics service logs
```

---

## 📝 **Environment Variables Checklist**

### **Backend (.env on Render):**
- [x] MONGO_URI
- [x] JWT_SECRET
- [x] ADMIN_LICENSE_KEY
- [x] ANALYTICS_SERVICE_URL
- [x] EMAIL_USER (optional)
- [x] EMAIL_PASS (optional)

### **Analytics (.env on Render):**
- [x] OPENAI_API_KEY
- [x] FLASK_ENV=production

### **Frontend (.env on Netlify):**
- [x] REACT_APP_API_URL

---

## 🎯 **For Your Capstone Defense**

### **Before Defense Day:**
1. ✅ Deploy all services (30 minutes)
2. ✅ Test thoroughly (upload datasets, check charts)
3. ✅ Note all URLs
4. ✅ Wake services 5 minutes before defense (visit URLs)
5. ✅ Prepare demo datasets
6. ✅ Have backup local version running

### **During Defense:**
- Show **live deployed version** (impressive! 🎉)
- Have **local version** as backup (in case internet issues)
- **URLs to share** with panel (let them test!)

### **Benefits of Deployed Version:**
- ✅ Proves production-readiness
- ✅ Panel can test on their devices
- ✅ Professional presentation
- ✅ Shows real cloud deployment
- ✅ Demonstrates technical competence

---

## 🔗 **Useful Links**

**Deployment Platforms:**
- Netlify: https://www.netlify.com
- Render: https://render.com
- MongoDB Atlas: https://www.mongodb.com/cloud/atlas
- OpenAI: https://platform.openai.com

**Documentation:**
- React: https://react.dev
- Express: https://expressjs.com
- Flask: https://flask.palletsprojects.com
- Mongoose: https://mongoosejs.com
- OpenAI API: https://platform.openai.com/docs

**Tutorials:**
- Deploy React to Netlify: https://docs.netlify.com/frameworks/react
- Deploy Node.js to Render: https://render.com/docs/deploy-node-express-app
- Deploy Python to Render: https://render.com/docs/deploy-flask

---

## 💼 **Alternative: One-Server Deployment**

**If panel asks about other options:**

"We could also deploy everything on a **single DigitalOcean droplet** for $6/month:
- Nginx serves the React frontend
- PM2 runs the Node.js backend
- Gunicorn runs the Python analytics
- All on one server with full control

This is more cost-effective for very small businesses, but we prefer the **microservices approach** because:
1. Each service can scale independently
2. Easier to maintain and debug
3. Better fault isolation
4. Industry best practice
5. Cloud-native architecture"

---

## 🎓 **Tech Stack Summary (For Quick Reference)**

| Layer | Technology | Why? |
|-------|-----------|------|
| **Frontend** | React 19 + TailwindCSS | Modern, responsive, component-based |
| **API Backend** | Node.js + Express 5 | Fast, JavaScript everywhere, huge ecosystem |
| **Analytics** | Python 3.12 + Flask | Data science standard, AI libraries |
| **Database** | MongoDB Atlas | Flexible, cloud-native, scalable |
| **AI Mapping** | OpenAI GPT-4o-mini | Intelligent, affordable ($0.0001/call) |
| **Forecasting** | Facebook Prophet | Industry-standard, accurate |
| **Hosting** | Netlify + Render | FREE tier, auto-deploy, professional |

---

## ✨ **Final Result**

After deployment, you'll have:

✅ **Professional live website** with HTTPS
✅ **Working AI analytics** with real OpenAI integration
✅ **Cloud database** with automatic backups
✅ **Public URLs** to share with anyone
✅ **Auto-deployment** from Git
✅ **$0/month hosting** (only pay for OpenAI usage)

**Perfect for demonstrating to your panel!** 🎉

---

**Ready to deploy? Follow the steps above and you'll have TANAW live in 30 minutes!** 🚀

*Questions? Check TANAW_TECH_STACK_AND_DEPLOYMENT.md for detailed explanations.*

