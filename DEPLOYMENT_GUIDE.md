# Asclepius AI Deployment Guide

## 🚀 Quick Deploy Status

### Current Deployment URLs:
- **Backend (Render)**: https://ideathon2026-clash-of-code.onrender.com
- **Frontend (Vercel)**: Will be deployed after backend is stable

---

## 📋 Deployment Steps

### 1. Backend Deployment on Render

#### Prerequisites:
- GitHub repository connected to Render
- Environment variables configured

#### Steps:

1. **Push the simplified server code**:
   ```bash
   git add server/main_deploy.py
   git add render.yaml
   git commit -m "Add simplified deployment server"
   git push origin main
   ```

2. **Render will automatically deploy using `render.yaml`**:
   - Uses `main_deploy.py` (simplified FastAPI server)
   - Only installs essential packages: `fastapi`, `uvicorn`, `python-dotenv`
   - Includes Telegram bot configuration

3. **Monitor deployment logs**:
   - Check https://dashboard.render.com for build status
   - Look for "Application startup complete" message

#### Environment Variables (Already Configured):
```yaml
TELEGRAM_BOT_TOKEN: 8795379419:AAG_fiiluEx-GQI1bHyisFaNuVxzsIMBFo8
TELEGRAM_NURSE_CHAT_ID: -5022062987  # Fixed chat ID
TELEGRAM_DOCTOR_CHAT_ID: -5294441613  # Working chat ID
```

#### API Endpoints Available:
- `GET /` - System status
- `GET /health` - Health check
- `GET /patients/` - List patients
- `POST /patients/{id}/trigger-critical` - **Trigger critical alerts + Telegram**
- `GET /alerts/` - List alerts
- `GET /protocols/pending` - Pending protocols
- `POST /seed/critical` - **Seed critical patients + Telegram notifications**

---

### 2. Frontend Deployment on Vercel

#### Current Issues Fixed:
- ✅ API URL updated to point to Render backend
- ✅ Missing `lib/api.js` resolved
- ✅ Build errors fixed

#### Deploy to Vercel:

1. **Connect to GitHub**:
   ```bash
   # Make sure all changes are committed
   git add .
   git commit -m "Fix API endpoints and deployment config"
   git push origin main
   ```

2. **Vercel Configuration** (`vercel.json`):
   ```json
   {
     "version": 2,
     "buildCommand": "cd client && npm install && npm run build",
     "outputDirectory": "client/dist",
     "framework": "vite",
     "env": {
       "VITE_API_URL": "https://ideathon2026-clash-of-code.onrender.com"
     },
     "rewrites": [
       { "source": "/(.*)", "destination": "/index.html" }
     ]
   }
   ```

3. **Deploy**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Import GitHub repository
   - Vercel will auto-detect React/Vite project
   - Deploy will start automatically

---

## 🔧 Key Fixes Applied

### 1. **Server Issues Fixed**:
- ❌ **Old Issue**: Beanie/MongoDB compilation errors on Render
- ✅ **Solution**: Created `main_deploy.py` with mock data and simple FastAPI
- ❌ **Old Issue**: Complex dependencies causing build failures
- ✅ **Solution**: Minimal requirements (only fastapi, uvicorn, python-dotenv)

### 2. **Client Issues Fixed**:
- ❌ **Old Issue**: Missing API functions (`getPendingProtocols`, `approveProtocol`)
- ✅ **Solution**: Complete API functions with fallback mock data in `lib/api.js`
- ❌ **Old Issue**: Build failing due to unresolved imports
- ✅ **Solution**: All imports resolved, API URL configured for production

### 3. **Telegram Issues Fixed**:
- ❌ **Old Issue**: Nurse chat ID (-5144644074) not found
- ✅ **Solution**: Updated to working chat ID (-5022062987)
- ❌ **Old Issue**: No buttons visible in Telegram
- ✅ **Solution**: Using direct notifications, critical button triggers Telegram

### 4. **Navigation Fixed**:
- ✅ **Landing Page**: Professional landing page at `/`
- ✅ **Dashboard**: Main ICU dashboard at `/dashboard`
- ✅ **Icons**: All navbar icons restored (⬡ ◈ ⊕ ≋)
- ✅ **Theme**: White theme support added

---

## 🧪 Testing the Deployment

### Backend Testing:
```bash
# Test system status
curl https://ideathon2026-clash-of-code.onrender.com

# Test critical alert (triggers Telegram)
curl -X POST https://ideathon2026-clash-of-code.onrender.com/patients/1/trigger-critical

# Test seed critical (triggers Telegram)
curl -X POST https://ideathon2026-clash-of-code.onrender.com/seed/critical
```

### Frontend Testing:
1. Visit deployed Vercel URL
2. Navigate to different pages using navbar
3. Test critical alert buttons
4. Check that data loads from backend API

---

## 📱 Telegram Bot Setup

### Bot Configuration:
- **Bot Token**: `8795379419:AAG_fiiluEx-GQI1bHyisFaNuVxzsIMBFo8`
- **Doctor Chat**: `-5294441613` ✅ Working
- **Nurse Chat**: `-5022062987` ✅ Updated

### Features:
- 🚨 Critical alerts → Doctor + Nurse
- ⚠️ Warning alerts → Nurse only
- 📋 Protocol notifications → Doctor for approval

### Testing Telegram:
1. Click "Critical Alert" button in dashboard
2. Use seed buttons in control panel
3. Check both doctor and nurse chats for notifications

---

## 🎨 White Theme

### Theme Toggle:
- Landing page has theme toggle button (☀️/🌙)
- Persists theme preference in localStorage
- Smooth transitions between themes

### Colors:
- **Dark**: Plasma cyan (#00f5d4) accents
- **Light**: Blue (#2563eb) accents
- **Backgrounds**: Automatic gradient adjustments

---

## 📊 Current Status

| Component | Status | URL |
|-----------|---------|-----|
| Backend API | ✅ Deployed | https://ideathon2026-clash-of-code.onrender.com |
| Frontend | 🔄 Ready to Deploy | Pending Vercel deployment |
| Database | ⚠️ Mock Data Mode | Using realistic medical mock data |
| Telegram Bot | ✅ Working | Doctor notifications working |
| Telegram Nurse | ⚠️ Fixed Chat ID | Updated to new working chat |

---

## 🚀 Next Steps

1. **Deploy Frontend to Vercel**
2. **Test full integration** (Frontend → Backend → Telegram)
3. **Monitor logs** for any issues
4. **Optional**: Restore full database functionality later

---

## 📞 Support

If deployment issues occur:
1. Check Render logs for backend errors
2. Check Vercel build logs for frontend errors
3. Test individual API endpoints
4. Verify Telegram bot permissions in both chats

**All configurations are now deployment-ready!** 🎉