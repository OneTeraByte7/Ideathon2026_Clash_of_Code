# 🏥 Asclepius AI - ICU Sepsis Early Warning System

**Complete Medical Alert System with Integrated Telegram Bot**

## ⚡ Quick Start - ONE COMMAND

```bash
# Start everything (Server + Telegram Bot + Database)
python start_system.py

# In another terminal, start frontend
cd client && npm run dev
```

Open http://localhost:5173 → Test alert buttons → Complete system operational! 🎉

## 🏗️ System Architecture  

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Client  │◄──►│  FastAPI Server │◄──►│  Telegram Bot   │
│   (Frontend)    │    │   (Backend)     │    │  (INTEGRATED)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
[Patient Dashboard]         [MongoDB Atlas]       [Doctor & Nurse Chats]
```

**✅ Integrated Design:**
- **Single Process**: Telegram bot runs inside FastAPI server
- **Shared Config**: One `.env` file for everything
- **Unified Logging**: All services log together
- **Graceful Shutdown**: Stop everything with Ctrl+C

## 🚀 Features

### **Critical Alert Workflow:**
1. **Website** → Click "🚨 CRITICAL ALERT" → Sends to **both** doctor & nurse
2. **Doctor** gets message with buttons: ✅ Approve | ❌ Reject | ✏️ Add Note  
3. **Nurse** gets status update and waits for doctor decision
4. **Doctor Response:**
   - **✅ Approve** → Nurse receives AI protocol immediately
   - **❌ Reject** → Doctor must use `/note PAT001 alternative treatment`
   - **✏️ Add Note** → Doctor provides modified instructions

### **Warning Alert Workflow:**  
1. **Website** → Click "⚠️ WARNING ALERT" → Sends **only to nurse**
2. **Nurse** receives monitoring alert (no approval needed)

## 📂 Project Structure

```
E:\Ideathon2026\
├── start_system.py           # 🚀 ONE COMMAND STARTUP
├── client\                   # React frontend  
│   ├── src\components\PatientCard.jsx  # Alert buttons
│   └── src\lib\api.js       # API calls
├── server\                   # FastAPI backend + Integrated Bot
│   ├── main.py              # Server with integrated Telegram bot
│   ├── services\
│   │   ├── telegram_service.py      # Notification service
│   │   └── telegram_bot_runner.py   # Integrated bot runner
│   ├── api\patients.py      # Alert endpoints  
│   └── .env                 # All configuration
└── TelegramBot\             # ⚠️ LEGACY - No longer needed!
```

## 🔧 Configuration

**All configuration in `server/.env`:**
```bash
# Telegram Integration (Required)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_NURSE_CHAT_ID=nurse_chat_id  
TELEGRAM_DOCTOR_CHAT_ID=doctor_chat_id

# Database (Already configured)
MONGODB_URL=mongodb+srv://...
GEMINI_API_KEY=AIzaSy...
```

## 🧪 Testing

```bash
# Test all connections
python test_connections.py

# Check system status  
curl http://localhost:8000

# Check integrated bot status
curl http://localhost:8000/telegram/bot/status
```

## 📱 Telegram Commands

**Doctor Commands:**
- `/note PAT001 your instructions here` - Send alternative treatment
- `/warning` - Test warning alert

**Workflow Example:**
```
1. Website: Click "Critical Alert"
2. Doctor receives: 🔴 CRITICAL ALERT with [Approve][Reject][Add Note]  
3. Doctor clicks "Reject"
4. Doctor types: /note PAT001 Start vancomycin instead
5. Nurse receives: 📝 DOCTOR'S ALTERNATIVE INSTRUCTIONS
```

## 🎯 Advantages of Integration

**Before (Separate Services):**
```bash
Terminal 1: python server/main.py
Terminal 2: python TelegramBot/telegram_bot.py  
Terminal 3: cd client && npm run dev
```

**Now (Integrated):**
```bash  
Terminal 1: python start_system.py
Terminal 2: cd client && npm run dev
```

**Benefits:**
- ✅ **Simpler deployment** - One service instead of two
- ✅ **Shared resources** - Same database connection, logging, config
- ✅ **Better error handling** - Unified error reporting
- ✅ **Easier monitoring** - Single health endpoint
- ✅ **Production ready** - No need to manage multiple processes

## 🏥 Ready for Medical Use

- **Real-time monitoring** with WebSocket updates
- **Production database** with MongoDB Atlas  
- **AI-powered risk scoring** with Gemini integration
- **Professional UI** with proper medical terminology
- **Complete audit trail** of all alerts and decisions
- **Telegram integration** for instant medical team notifications

**System operational and ready for ICU deployment! 🚀**