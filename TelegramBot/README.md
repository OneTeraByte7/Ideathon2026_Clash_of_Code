# 🤖 Telegram Bot Setup for Asclepius AI

## Installation

1. **Install Python dependencies**:
```bash
cd TelegramBot
pip install python-telegram-bot httpx
```

2. **Run the bot**:
```bash
python asclepius_bot.py
```

## Features

### For Doctors 👨‍⚕️
- **Inline Buttons** on critical protocol alerts:
  - ✅ **Approve Protocol** - Approve and activate treatment
  - ❌ **Reject Protocol** - Reject with feedback option
  - ✏️ **Modify Protocol** - Request changes
  - 📋 **View Details** - Link to full protocol details

### Commands
- `/start` - Bot introduction and help
- `/help` - Show available commands  
- `/note <protocol_id> <your_note>` - Add doctor notes to protocols

### Example Usage
```
Doctor receives alert:
📋 MEDICAL PROTOCOL GENERATED
Patient: Ramesh Kulkarni (ICU-01)
Risk Score: 87.5
[Buttons: Approve | Reject | Modify | Details]

Doctor clicks "Approve" → Protocol is approved in system
Doctor clicks "Modify" → Bot asks for /note command
Doctor sends: /note 123 Increase antibiotic dose
```

## Configuration

Edit `asclepius_bot.py` to update:
- `BOT_TOKEN` - Your bot token from @BotFather
- `DOCTOR_CHAT_ID` - Doctor group chat ID  
- `API_BASE_URL` - Your deployed API URL

## Running in Production

### Option 1: Local Server
```bash
# Keep bot running in background
nohup python asclepius_bot.py > bot.log 2>&1 &
```

### Option 2: Deploy to Heroku/Railway
1. Create `requirements.txt`:
```
python-telegram-bot>=20.0
httpx>=0.25.0
```

2. Create `Procfile`:
```
worker: python asclepius_bot.py
```

3. Deploy as a worker process (not web service)

### Option 3: Run on Same Server as API
Add to your main server startup script or run as separate process.

## Testing

1. Add the bot to your doctor group
2. Send a test protocol alert from the dashboard  
3. Click buttons to test responses
4. Check logs for successful API calls

🏥 **The bot will now handle all doctor protocol responses!**