# 🧪 Local Testing Guide for TANAW

## 🎯 Why Test Locally?

Testing locally allows you to:
- ✅ See emails instantly (using Ethereal fake SMTP)
- ✅ Debug issues faster
- ✅ Test without deploying
- ✅ Verify features work before production

---

## 📋 Prerequisites

Make sure you have:
- ✅ Node.js installed
- ✅ MongoDB running locally OR MongoDB Atlas connection
- ✅ Python 3.11 installed (for Flask)
- ✅ All dependencies installed

---

## 🚀 Step 1: Setup Backend (Node.js)

### 1.1 Navigate to backend folder
```powershell
cd backend
```

### 1.2 Create `.env` file (if not exists)
```powershell
# In backend folder, create .env file with:
```

**`backend/.env`:**
```env
# MongoDB
MONGO_URI=mongodb://localhost:27017/tanaw
# OR use MongoDB Atlas:
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/tanaw

# JWT Secret
JWT_SECRET=your_super_secret_jwt_key_here_change_in_production

# Admin License Key
ADMIN_LICENSE_KEY=TANAW2025ADMIN

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Email Configuration (for local testing - uses Ethereal fake SMTP)
EMAIL_SERVICE=development
# Leave EMAIL_SERVICE empty or set to "development" for testing

# For production emails (when ready):
# EMAIL_SERVICE=gmail
# EMAIL_USER=tanawofficial@gmail.com
# EMAIL_PASSWORD=your_gmail_app_password
# EMAIL_FROM=tanawofficial@gmail.com

# Flask Analytics Service
FLASK_ANALYTICS_URL=http://localhost:5001

# OpenAI API Key (for AI features)
OPENAI_API_KEY=your_openai_api_key_here
```

### 1.3 Install dependencies
```powershell
npm install
```

### 1.4 Start backend server
```powershell
npm run dev
```

**You should see:**
```
✅ Server running on http://localhost:5000
✅ MongoDB connected
```

---

## 🚀 Step 2: Setup Frontend (React)

### 2.1 Open NEW terminal, navigate to frontend
```powershell
cd frontend
```

### 2.2 Create `.env.local` file
```powershell
# In frontend folder, create .env.local file
```

**`frontend/.env.local`:**
```env
REACT_APP_RECAPTCHA_SITE_KEY=6LdL4cErAAAAAN4Nh_3VBouHliMIKc47QAEx7AK_
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ANALYTICS_API_URL=http://localhost:5000/api
```

### 2.3 Install dependencies
```powershell
npm install
```

### 2.4 Start frontend server
```powershell
npm start
```

**Browser should open automatically at:** `http://localhost:3000`

---

## 🚀 Step 3: Setup Flask Analytics (Optional)

### 3.1 Open NEW terminal, navigate to analytics service
```powershell
cd backend\analytics_service
```

### 3.2 Create virtual environment
```powershell
python -m venv venv
```

### 3.3 Activate virtual environment
```powershell
.\venv\Scripts\activate
```

### 3.4 Install dependencies
```powershell
pip install -r requirements.txt
```

### 3.5 Start Flask server
```powershell
python app.py
```

**You should see:**
```
✅ Flask running on http://localhost:5001
```

---

## 📧 Step 4: Testing Emails Locally

### How Emails Work Locally:

When `EMAIL_SERVICE` is NOT set (or set to "development"), TANAW uses **Ethereal Email** - a fake SMTP server perfect for testing!

### Testing Email Features:

#### 1️⃣ **Test Welcome Email (Registration)**

1. Go to: `http://localhost:3000/register`
2. Register a new user
3. **Check backend console** - you'll see:
   ```
   📧 Using Ethereal test email account: [email]
   📧 Preview URL: https://ethereal.email/message/xxxxx
   ✅ Welcome email sent to: [your-email]
   ```
4. **Click the Preview URL** to see the email in browser!

#### 2️⃣ **Test Account Deletion Email**

1. Login as admin: `http://localhost:3000/admin-login`
   - Email: `admin@tanawofficial.com`
   - Password: your admin password
   - License Key: `TANAW2025ADMIN`

2. Go to **Active Users** tab
3. Click **Actions** → **Delete User**
4. **Check backend console** for Preview URL
5. Click URL to see deletion email

#### 3️⃣ **Test Email Change Verification**

1. Login as regular user: `http://localhost:3000/login`
2. Click profile icon → **Edit Profile**
3. Change email address
4. Click **Save Changes**
5. **Check backend console** for 2 Preview URLs:
   - Verification email (to new email)
   - Notification email (to old email)

#### 4️⃣ **Test Password Reset Email**

1. Go to: `http://localhost:3000/forgot-password`
2. Enter email address
3. **Check backend console** for Preview URL
4. Click URL to see password reset email
5. Test the reset link!

---

## 🧪 Testing Checklist

### Frontend Features:
- [ ] **Registration** - Form clears after submit ✅
- [ ] **Login** - Successfully logs in ✅
- [ ] **Filters** - Role/Date/Search all clickable ✅
- [ ] **Actions Dropdown** - Click to open ✅
- [ ] **Delete User** - Removes from list immediately ✅
- [ ] **Date Filter** - Filters by date range ✅
- [ ] **Edit Profile** - Saves changes ✅
- [ ] **Change Email** - Shows verification message ✅

### Backend Features:
- [ ] **Registration API** - Returns success ✅
- [ ] **Welcome Email** - Sends automatically 📧
- [ ] **Delete User API** - Returns success ✅
- [ ] **Deletion Email** - Sends automatically 📧
- [ ] **Email Change API** - Generates token ✅
- [ ] **Verification Email** - Sends to new email 📧
- [ ] **Notification Email** - Sends to old email 📧
- [ ] **Password Reset** - Sends reset link 📧

---

## 🐛 Troubleshooting

### Problem: Backend not connecting to MongoDB

**Solution:**
```powershell
# Start MongoDB locally
mongod

# OR use MongoDB Atlas connection string in .env
```

### Problem: "Email failed to send"

**Solution:**
- Check backend console for errors
- Make sure `EMAIL_SERVICE` is NOT set (or set to "development")
- If using Gmail, make sure you created an App Password

### Problem: Frontend can't reach backend

**Solution:**
- Make sure backend is running on port 5000
- Check `REACT_APP_API_URL` in `frontend/.env.local`
- Clear browser cache (Ctrl + Shift + Delete)

### Problem: "User not found" after deletion

**Solution:**
- This is already fixed in the latest code
- Frontend now removes user from list immediately
- Make sure you uploaded the latest build to Hostinger

---

## 📊 Console Logs to Watch

### Backend Console (Important logs):
```
✅ Server running on http://localhost:5000
✅ MongoDB connected
📧 Using Ethereal test email account: [email]
📧 Preview URL: https://ethereal.email/message/xxxxx
✅ Welcome email sent to: [email]
✅ Account deletion notification sent to: [email]
✅ Email verification sent to: [email]
```

### Frontend Console (Important logs):
```
📂 Loading user datasets from backend...
📂 Loaded 56 datasets from backend
✅ User deleted successfully
📊 Tracked chart generation: bar
```

---

## 🎯 Production vs Development

| Feature | Development (Local) | Production (Railway/Hostinger) |
|---------|-------------------|-------------------------------|
| Backend URL | `http://localhost:5000` | `https://tanawv2-production.up.railway.app` |
| Frontend URL | `http://localhost:3000` | `https://your-domain.com` |
| Email Service | Ethereal (Fake SMTP) | Gmail (Real emails) |
| MongoDB | Local/Atlas | MongoDB Atlas |
| Flask Service | `http://localhost:5001` | Railway deployment |

---

## 🚀 After Testing Locally - Deploy to Production

When everything works locally:

### 1. Backend (Railway)
```powershell
git add .
git commit -m "Add welcome email and fix email notifications"
git push origin main
```

Railway auto-deploys from GitHub!

### 2. Frontend (Hostinger)
```powershell
cd frontend
$env:REACT_APP_API_URL="https://tanawv2-production.up.railway.app/api"
$env:REACT_APP_ANALYTICS_API_URL="https://tanawv2-production.up.railway.app/api"
npm run build
```

Upload `frontend\build\` to Hostinger!

---

## 📧 Switching to Real Emails (Gmail)

When ready for production emails:

1. **Get Gmail App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Create app password for "TANAW"
   - Copy the 16-character password

2. **Update Railway Environment Variables:**
   ```
   EMAIL_SERVICE=gmail
   EMAIL_USER=tanawofficial@gmail.com
   EMAIL_PASSWORD=[your-16-char-app-password]
   EMAIL_FROM=tanawofficial@gmail.com
   ```

3. **Restart Railway service**

4. **Test!** Emails will now send to REAL email addresses! 📧

---

## ✅ You're Ready!

Now you can:
- ✅ Test all features locally before deployment
- ✅ See emails instantly using Ethereal
- ✅ Debug issues faster
- ✅ Deploy with confidence!

---

**Need help?** Check the backend console for detailed logs! 🚀

