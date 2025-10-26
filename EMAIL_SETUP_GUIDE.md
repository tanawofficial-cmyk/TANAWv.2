# 📧 Email Configuration for TANAW

## ⚠️ Email Not Working? Here's Why:

Your email service needs to be configured on Railway for these features to work:
- ✅ Password reset emails
- ✅ Email change verification
- ✅ Account deletion notifications
- ✅ Contact form notifications

---

## 🔧 How to Configure Email on Railway:

### Option 1: Gmail (Easiest for Testing)

#### Step 1: Create Gmail App Password

1. **Go to your Google Account:** https://myaccount.google.com
2. **Enable 2-Step Verification** (Security → 2-Step Verification)
3. **Create App Password:**
   - Security → 2-Step Verification → App Passwords
   - Select app: Mail
   - Select device: Other (Custom name: TANAW)
   - Click Generate
   - **Copy the 16-character password**

#### Step 2: Add to Railway Environment Variables

**Go to Railway Dashboard → tanawv2-production → Variables:**

```bash
EMAIL_SERVICE=gmail
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_FROM=noreply@tanaw.com
```

**Example:**
```
EMAIL_SERVICE=gmail
EMAIL_USER=tanawofficial@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
EMAIL_FROM=TANAW Support <noreply@tanaw.com>
```

---

### Option 2: Custom SMTP (For Production)

**For services like SendGrid, Mailgun, etc.:**

```bash
EMAIL_SERVICE=smtp
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
EMAIL_FROM=noreply@yourdomain.com
```

---

## 📋 Required Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `EMAIL_SERVICE` | Email provider | `gmail` or `smtp` |
| `EMAIL_USER` | Your email address | `tanawofficial@gmail.com` |
| `EMAIL_PASSWORD` | App password (Gmail) | `abcd efgh ijkl mnop` |
| `EMAIL_FROM` | From address | `TANAW Support <noreply@tanaw.com>` |

**For SMTP (if not Gmail):**
| Variable | Description | Example |
|----------|-------------|---------|
| `SMTP_HOST` | SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_SECURE` | Use SSL/TLS | `false` |
| `SMTP_USER` | SMTP username | Your email |
| `SMTP_PASSWORD` | SMTP password | Your app password |

---

## 🧪 Testing Email Configuration:

### After Adding Variables to Railway:

1. **Wait 1-2 minutes** for backend to restart
2. **Test password reset:**
   - Go to login page
   - Click "Forgot Password"
   - Enter email
   - Check if email arrives

3. **Test account deletion:**
   - Admin dashboard → Delete a user
   - Check user's email inbox
   - Should receive deletion notification

4. **Test email change:**
   - User profile → Edit → Change email
   - Check new email inbox
   - Should receive verification link

---

## 🐛 Troubleshooting:

### Issue: No Emails Received

**Check Railway Logs:**
1. Railway Dashboard → tanawv2-production → Deployments
2. View Logs
3. Look for email-related errors

**Common Errors:**
```
❌ Error sending email: Invalid login
→ Check EMAIL_USER and EMAIL_PASSWORD are correct

❌ Error sending email: Connection timeout
→ Check SMTP_HOST and SMTP_PORT

❌ No email service configured
→ Check EMAIL_SERVICE variable is set
```

### Issue: Gmail App Password Not Working

**Make sure:**
- ✅ 2-Step Verification is enabled
- ✅ Using App Password (not regular password)
- ✅ No spaces in the password (or include them exactly as shown)
- ✅ EMAIL_SERVICE=gmail is set

### Issue: Emails Go to Spam

**This is normal for development!**
- Check spam folder
- In production, use proper email service (SendGrid, AWS SES)
- Configure SPF/DKIM records for your domain

---

## 📝 Quick Setup (Gmail):

```bash
# 1. Get Gmail App Password (16 characters)
# https://myaccount.google.com/apppasswords

# 2. Add to Railway (tanawv2-production service):
EMAIL_SERVICE=gmail
EMAIL_USER=tanawofficial@gmail.com
EMAIL_PASSWORD=your-app-password-here
EMAIL_FROM=TANAW Support <noreply@tanaw.com>

# 3. Wait 2 minutes for restart

# 4. Test by deleting a user or resetting password
```

---

## ✅ Success Indicators:

You know emails are working when:
- ✅ Password reset emails arrive
- ✅ Email change verification emails arrive
- ✅ Account deletion notifications arrive
- ✅ Contact form emails arrive
- ✅ No email errors in Railway logs

---

## 🚀 For Production:

**Don't use Gmail in production!** Use:
- ✅ **SendGrid** (Recommended, free tier available)
- ✅ **AWS SES** (Cheap, reliable)
- ✅ **Mailgun** (Easy to set up)
- ✅ **Postmark** (Excellent deliverability)

**Gmail Limitations:**
- ❌ 500 emails/day limit
- ❌ May be blocked by some providers
- ❌ Not designed for transactional emails

---

## 📧 Email Features in TANAW:

### Currently Implemented:
1. ✅ **Password Reset** - Sends reset link to user
2. ✅ **Password Change Confirmation** - Notifies user of password change
3. ✅ **Email Change Verification** - Sends verification to new email
4. ✅ **Email Change Notification** - Notifies old email of change
5. ✅ **Account Deletion** - Notifies user when account deleted
6. ✅ **Contact Form** - Sends to admin and confirms to user

### Email Templates:
All emails use professional HTML templates with:
- ✅ TANAW branding
- ✅ Responsive design
- ✅ Security warnings
- ✅ Plain text fallback

---

## 🎯 TL;DR - Quick Email Setup:

1. **Get Gmail App Password:** https://myaccount.google.com/apppasswords
2. **Add to Railway Variables:**
   ```
   EMAIL_SERVICE=gmail
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   ```
3. **Wait 2 minutes** for restart
4. **Test** by deleting a user

---

**Set this up on Railway NOW to enable all email features!** 📧🚀

