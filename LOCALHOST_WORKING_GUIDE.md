# 🏥 ASCLEPIUS AI - COMPLETE LOCALHOST SETUP GUIDE

## 🚀 Quick Start (30 seconds)

### 1. Start Backend Server
```bash
cd E:\Ideathon2026
python start_server_simple.py
```

### 2. Start Frontend Client  
```bash
cd E:\Ideathon2026\client
npm run dev
```

### 3. Open Browser
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## 📱 TELEGRAM CONFIGURATION (REAL MODE)

Your Telegram is **PROPERLY CONFIGURED** with:
- ✅ Bot Token: `8795379419:AAG_fiiluEx-GQI1bHyisFaNuVxzsIMBFo8`
- ✅ Doctor Chat: `-5294441613` (WORKING)
- ✅ Nurse Chat: `-5022062987` (NEW - Updated)

### 🔧 Environment Variables (Already Set)
```bash
TELEGRAM_BOT_TOKEN=8795379419:AAG_fiiluEx-GQI1bHyisFaNuVxzsIMBFo8
TELEGRAM_DOCTOR_CHAT_ID=-5294441613  
TELEGRAM_NURSE_CHAT_ID=-5022062987
```

## 🧪 TEST TELEGRAM NOTIFICATIONS

### 1. Test via API
```bash
curl http://localhost:8000/telegram/test
```

### 2. Test via Critical Alert  
1. Go to ICU Grid page
2. Click **"CRITICAL ALERT"** button on any patient
3. Check Telegram groups for messages

### 3. Expected Messages
- **Nurse Group**: Gets warning + critical alerts
- **Doctor Group**: Gets critical alerts + action buttons

## 🐛 FIXES APPLIED

### ✅ Server Issues Fixed
1. **Import Errors**: Removed duplicate imports in `main.py`
2. **Directory Issues**: Created `start_server_simple.py` for proper startup
3. **Telegram Configuration**: Real mode enabled (no demo mode)

### ✅ Client Issues Fixed  
1. **React Key Errors**: Fixed unique key generation in AlertsPage
2. **Object Rendering**: Safe object-to-string conversion
3. **Export Errors**: Verified `triggerCriticalAlert` export in `api.js`

### ✅ AlertsPage Errors Fixed
1. **"Objects not valid as React child"**: Fixed message rendering
2. **Duplicate keys**: Enhanced unique key generation  
3. **Type safety**: Added Boolean() conversions for notification status

## 📁 FILE STRUCTURE

```
E:\Ideathon2026\
├── server/
│   ├── main.py                 # ✅ Fixed imports
│   ├── .env                    # ✅ Real Telegram config
│   ├── services/telegram_service.py  # ✅ Real mode
│   └── api/                    # ✅ All working
├── client/
│   ├── src/pages/AlertsPage.jsx  # ✅ Fixed React errors
│   ├── src/lib/api.js           # ✅ All exports working
│   └── src/components/          # ✅ All working
├── start_server_simple.py      # ✅ NEW - Reliable startup
└── test_server.py              # ✅ NEW - Import testing
```

## 🎯 CRITICAL WORKFLOW TEST

### Complete Test Sequence:
1. **Start servers** (both backend + frontend)
2. **Open** http://localhost:5173
3. **Navigate** to ICU Grid  
4. **Click** "CRITICAL ALERT" on any patient
5. **Check** both Telegram groups for messages
6. **Verify** doctor gets action buttons in Telegram

### Expected Results:
- ✅ Nurse group gets notification
- ✅ Doctor group gets notification with buttons  
- ✅ Frontend shows alert in Alerts tab
- ✅ No console errors in browser
- ✅ WebSocket connection working

## 🔍 TROUBLESHOOTING

### If Server Won't Start:
```bash
cd E:\Ideathon2026
python test_server.py  # Test imports first
```

### If Telegram Not Working:
1. Check bot is in both groups
2. Check group chat IDs are negative numbers
3. Test: `curl http://localhost:8000/telegram/config`

### If Frontend Errors:
1. Clear browser cache
2. Check console for specific errors
3. Verify API endpoints: http://localhost:8000/docs

## 🏆 SUCCESS INDICATORS

- ✅ Server starts without import errors
- ✅ Frontend loads without React errors  
- ✅ WebSocket connects (green "LIVE" indicator)
- ✅ Critical alerts trigger Telegram messages
- ✅ Doctor gets interactive buttons in Telegram
- ✅ No object rendering errors in AlertsPage

---
🏥 **Asclepius AI v2.0** - Professional Medical Monitoring System
📱 **Real Telegram Integration** - No Demo Mode
⚡ **Full Featured** - Ready for Medical Use