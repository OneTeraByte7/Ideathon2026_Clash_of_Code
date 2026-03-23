# 🚀 Complete System Startup Guide

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   React Client  │◄──►│  FastAPI Server │◄──►│  Telegram Bot   │
│   (Frontend)    │    │   (Backend)     │    │   (Notifications)│
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         v                       v                       v
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  WebSocket      │    │   MongoDB       │    │ Doctor & Nurse  │
│  Real-time      │    │   Database      │    │  Telegram Chats │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites ✅

- **Python 3.8+** installed
- **Node.js 16+** and npm installed  
- **MongoDB Atlas** account (or local MongoDB)
- **Telegram Bot Token** from @BotFather
- **Telegram Chat IDs** for doctor and nurse

# 🚀 SIMPLIFIED STARTUP - Single Command

## ONE COMMAND TO START EVERYTHING! 🎉

```bash
cd E:\Ideathon2026

# This starts EVERYTHING - Server + Telegram Bot integrated!
python start_system.py
```

**Expected Output:**
```
🏥 ASCLEPIUS AI - ICU SEPSIS EARLY WARNING SYSTEM
🚀 Single Command Startup - Everything Integrated

🔧 Checking requirements...
✅ All Python dependencies found
🚀 Starting integrated server with Telegram bot...
🚀 Starting Asclepius AI system...
✅ Database connected
📱 Telegram service initialized with real mode
✅ Telegram bot connected: YourBotName
🤖 Integrated Telegram bot started successfully
✅ Telegram bot started successfully
📱 Nurse Chat ID: -5022062987
👨‍⚕️ Doctor Chat ID: -5294441613

🌐 Server starting on http://localhost:8000
🏥 ASCLEPIUS AI SYSTEM OPERATIONAL
```

**Then start frontend in another terminal:**
```bash
cd E:\Ideathon2026\client
npm run dev
```

That's it! Everything runs under one command! 🎯

---

# 🔧 Manual Startup (Old Method)

If you prefer to run services separately:

## Step 2: Start Backend Server 🖥️

```bash
cd E:\Ideathon2026\server

# Install dependencies
pip install -r requirements.txt

# Initialize database with sample data
python seed_patients.py

# Start the FastAPI server (now includes Telegram bot!)
python main.py
```

**Expected Output:**
```
🚀 Starting Asclepius AI system...
✅ Database connected
📱 Telegram service initialized with real mode  
✅ Telegram bot connected: YourBotUsername
🤖 Integrated Telegram bot started successfully
INFO: Uvicorn running on http://0.0.0.0:8000
```

~~## Step 3: Start Telegram Bot 🤖~~

**⚠️ NO LONGER NEEDED! Telegram bot now runs integrated with the server!**

## Step 4: Start Frontend Client 🌐

```bash
cd E:\Ideathon2026\client

# Install dependencies
npm install

# Start the development server
npm run dev
```

**Expected Output:**
```
Local:   http://localhost:5173/
Network: use --host to expose
```

## Step 5: Test Complete Integration 🧪

### 5.1 Verify System Status
1. **Backend Health:** http://localhost:8000/health
2. **Frontend:** http://localhost:5173  
3. **API Docs:** http://localhost:8000/docs

### 5.2 Test Critical Alert Workflow

1. **Open Frontend** → Go to Dashboard
2. **Find a Patient Card** → Click "🚨 CRITICAL ALERT" button  
3. **Check Telegram Chats:**
   - **Nurse Chat:** Should receive waiting message
   - **Doctor Chat:** Should receive message with buttons

4. **Doctor Response Test:**
   ```
   Doctor clicks: ✅ Approve
   → Nurse should receive AI protocol instructions
   
   OR
   
   Doctor clicks: ❌ Reject  
   → Doctor types: /note PAT001 Alternative treatment plan
   → Nurse should receive doctor's alternative instructions
   ```

### 5.3 Test Warning Alert Workflow

1. **Find a Patient Card** → Click "⚠️ WARNING ALERT" button
2. **Check Nurse Chat:** Should receive warning (doctor gets nothing)

## Step 6: Verify Database Connection 💾

```bash
# Check patients exist
curl http://localhost:8000/patients/

# Check alerts  
curl http://localhost:8000/alerts/

# Seed more test data
curl -X POST http://localhost:8000/seed/critical
```

## Troubleshooting 🔧

### Backend Won't Start
```bash
# Check Python dependencies
pip list | grep fastapi

# Check MongoDB connection
python -c "import motor.motor_asyncio; print('✅ Motor installed')"

# Check port availability  
netstat -an | find "8000"
```

### Telegram Bot Issues
```bash
# Test bot token
curl https://api.telegram.org/bot8795379419:AAG_fiiluEx-GQI1bHyisFaNuVxzsIMBFo8/getMe

# Check if bot is in chats
# Send /start in both nurse and doctor chats
```

### Frontend Connection Issues
```bash
# Check if backend is accessible
curl http://localhost:8000/health

# Check WebSocket connection in browser console
# Should see: "Connecting to WebSocket: ws://localhost:8000/ws/icu"
```

### Database Issues  
```bash
# Re-seed database
cd server
python seed_patients.py

# Check MongoDB Atlas connection
# Login to https://cloud.mongodb.com
# Verify Asclepius database has 4 collections
```

## System URLs 📍

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | Main dashboard |
| **Backend API** | http://localhost:8000 | REST API |  
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | System status |
| **WebSocket** | ws://localhost:8000/ws/icu | Real-time updates |

## Expected File Structure 📁

```
E:\Ideathon2026\
├── client\                    # React frontend
│   ├── src\
│   │   ├── components\PatientCard.jsx  # With both alert buttons  
│   │   ├── lib\api.js         # API functions
│   │   └── pages\Dashboard.jsx # Main dashboard
│   └── package.json
├── server\                    # FastAPI backend  
│   ├── api\patients.py        # With trigger-critical & trigger-warning endpoints
│   ├── services\telegram_service.py  # Telegram integration
│   ├── main.py               # Server entry point
│   └── .env                  # Environment configuration  
└── TelegramBot\              # Telegram bot
    ├── telegram_bot.py       # Bot with complete workflow
    ├── requirements.txt      # Bot dependencies
    └── README.md            # Bot setup guide
```

## Success Indicators ✅

**System is fully connected when:**

1. ✅ Server starts and shows "🤖 Integrated Telegram bot started successfully"
2. ✅ Frontend loads dashboard with patient cards
3. ✅ Critical alert button sends to both doctor & nurse  
4. ✅ Warning alert button sends only to nurse
5. ✅ Doctor buttons work (approve/reject/note)  
6. ✅ `/note PAT001 message` sends instructions to nurse
7. ✅ Everything runs under ONE command: `python start_system.py`

**Complete medical alert system operational with single command startup! 🏥✨**