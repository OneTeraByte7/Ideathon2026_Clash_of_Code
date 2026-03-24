# Asclepius AI - Telegram Bot (Production)

## 🏥 Medical Alert Telegram Bot System

Production-ready Telegram bot for the Asclepius AI ICU Sepsis Early Warning System. Handles critical medical protocol approvals and real-time notifications for healthcare staff.

## 🚀 Features

- **Critical Sepsis Alerts**: Real-time notifications with doctor approval workflow
- **Protocol Management**: Approve, reject, or modify AI-generated medical protocols
- **Medical Team Communication**: Secure communication between doctors and nurses
- **Production-Grade**: No demo mode - built for actual medical use
- **Error Handling**: Robust error handling and logging

## 🔧 Setup & Configuration

### 1. Environment Variables

Create a `.env` file in the server directory with:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_NURSE_CHAT_ID=-your_nurse_chat_id
TELEGRAM_DOCTOR_CHAT_ID=-your_doctor_chat_id
```

### 2. Bot Setup

1. Create a bot with [@BotFather](https://t.me/BotFather)
2. Get the bot token and add to `.env`
3. Add the bot to your doctor and nurse groups
4. Get chat IDs using [@userinfobot](https://t.me/userinfobot)

### 3. Installation

```bash
cd TelegramBot
pip install -r requirements.txt
```

## 🏃‍♂️ Running the Bot

### Standalone Mode
```bash
python telegram_bot.py
```

### Integrated with Server
The bot runs automatically when you start the main server:
```bash
cd ../server
python main.py
```

## 📱 Bot Commands

### For Doctors
- `/start` - Show bot information and role
- `/note PAT001 instructions` - Send treatment instructions
- `/status` - Check system status
- `/help` - Show detailed help

### For Nurses  
- `/start` - Show bot information
- `/status` - Check system status

### Button Actions (Doctors Only)
- ✅ **Approve**: Execute AI protocol immediately
- ❌ **Reject**: Provide alternative treatment plan
- ✏️ **Modify**: Adjust protocol with specific changes

## 🔄 Workflow

### Critical Alert Workflow
1. System detects critical sepsis risk
2. Doctor receives alert with approval buttons
3. Doctor chooses: Approve, Reject, or Modify
4. Nursing staff receives immediate implementation instructions

### Protocol Management
```
AI Detection → Doctor Alert → Decision → Nurse Instructions → Implementation
```

## 📝 Usage Examples

### Approving Protocol
Doctor receives alert → Clicks "✅ Approve" → Nurse gets implementation instructions

### Rejecting Protocol
Doctor receives alert → Clicks "❌ Reject" → Uses `/note PAT001 alternative instructions`

### Modifying Protocol  
Doctor receives alert → Clicks "✏️ Modify" → Uses `/note PAT001 specific modifications`

### General Instructions
```
/note PAT001 Start vancomycin 1g q12h, hold piperacillin
/note PAT002 Increase fluid to 150ml/hr, check lactate q2h
/note PAT003 Add norepinephrine if MAP < 65, call if no improvement
```

## 🔐 Security Features

- **Chat ID Validation**: Only authorized chats can interact
- **Role-Based Access**: Doctors and nurses have different permissions
- **Secure Messaging**: All communications are encrypted by Telegram
- **Error Logging**: Comprehensive logging for debugging

## 🏥 Production Considerations

### Medical Grade Features
- **Time-Critical Alerts**: Immediate notification system
- **Audit Trail**: All decisions are logged with timestamps
- **Redundant Messaging**: Multiple confirmation layers
- **Professional Formatting**: Clear, medical-standard communications

### Reliability
- **Connection Monitoring**: Auto-reconnection on failures
- **Error Recovery**: Graceful handling of API issues
- **Status Monitoring**: Real-time system health checks
- **Failover**: Falls back to logging if Telegram is unavailable

## 🐛 Troubleshooting

### Common Issues

**Bot not responding:**
```bash
# Check token validity
curl https://api.telegram.org/bot<TOKEN>/getMe
```

**Chat ID issues:**
1. Add bot to group
2. Send `/start` command
3. Check logs for chat ID
4. Update .env file

**Permission errors:**
1. Ensure bot is admin in groups
2. Check bot can send messages
3. Verify chat IDs are correct (negative for groups)

### Debug Commands
```bash
# Test bot status
python -c "from telegram_bot import AsclepiusTelegramBot; bot = AsclepiusTelegramBot(); print('Configured:', bot.is_configured())"

# Check configuration
python -c "from server.config import get_settings; s = get_settings(); print('Token:', bool(s.telegram_bot_token)); print('Nurse:', s.telegram_nurse_chat_id); print('Doctor:', s.telegram_doctor_chat_id)"
```

## 📊 Monitoring

The bot provides real-time status information:
- Active connections
- Message delivery status  
- Error rates and types
- Protocol processing metrics

Use `/status` command for health checks.

## 🔄 Updates & Maintenance

### Regular Tasks
- Monitor error logs
- Verify chat connectivity
- Update bot token if needed
- Review message delivery metrics

### Security Updates
- Keep python-telegram-bot updated
- Monitor Telegram API changes
- Review access permissions regularly

## 📞 Support

For medical emergencies, contact ICU staff directly. For technical issues:
1. Check logs in server console
2. Verify network connectivity  
3. Test bot with `/status` command
4. Contact system administrator

---

**⚠️ Important**: This is a medical alert system. Ensure proper testing before production use in healthcare environments.