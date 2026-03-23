# 🤖 Telegram Bot Setup for Asclepius AI

## NEW WORKFLOW IMPLEMENTATION

### Critical Alert Workflow:
1. **Website → Critical Alert Button** → Sends alert to both Doctor and Nurse
2. **Doctor receives** message with buttons: ✅ Approve, ❌ Reject, ✏️ Add Note
3. **If Approved** → Nurse receives AI recommendation to implement immediately
4. **If Rejected** → Nurse notified to wait, Doctor must add note with `/note PAT001 alternative instructions`
5. **If Note Added** → Doctor's alternative instructions sent to nurse

### Warning Alert Workflow:
1. **Website → Warning Button** → Sends alert to Nurse only (no approval needed)

## Installation

1. **Install Python dependencies**:
```bash
cd TelegramBot
pip install -r requirements.txt
```

2. **Setup Environment Variables in server/.env**:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_DOCTOR_CHAT_ID=doctor_chat_id_here  
TELEGRAM_NURSE_CHAT_ID=nurse_chat_id_here
```

3. **Run the bot**:
```bash
python telegram_bot.py
```

## Features

### For Doctors 👨‍⚕️
- **Critical Alert Buttons**:
  - ✅ **Approve** - Send AI protocol to nurse immediately
  - ❌ **Reject** - Reject protocol, nurse waits for alternative
  - ✏️ **Add Note** - Modify protocol with custom instructions

### For Nurses 👩‍⚕️
- **Receive Critical Alerts** with status updates
- **Receive Warning Alerts** for monitoring
- **Get AI Recommendations** when doctor approves
- **Receive Alternative Instructions** when doctor rejects/modifies

## Commands
- `/note <patient_id> <message>` - Doctor adds notes/instructions after rejection or modification
- `/warning` - Test warning alert (for testing)

## Example Workflow

### Critical Alert Example:
```
🔴 CRITICAL ALERT - Doctor Action Required
Patient: John Doe (Bed 3)
Risk Score: 87.5/100
📋 AI-Generated Protocol Ready

[✅ Approve] [❌ Reject] [✏️ Add Note]
```

**If Doctor clicks "Approve":**
```
Nurse receives:
✅ AI PROTOCOL APPROVED
Patient ID: PAT001
🤖 AI RECOMMENDATION:
• Immediate blood cultures
• Start empirical antibiotics (Vancomycin + Piperacillin-Tazobactam)
• Fluid resuscitation 30ml/kg crystalloid
• Monitor lactate q1h
```

**If Doctor clicks "Reject":**
```
Nurse receives:
❌ PROTOCOL REJECTED  
Patient ID: PAT001
⏳ Please wait for doctor's alternative instructions

Doctor then types: /note PAT001 Start vancomycin only, hold fluids

Nurse receives:
📝 DOCTOR'S ALTERNATIVE INSTRUCTIONS
Patient ID: PAT001
👨‍⚕️ Instructions: Start vancomycin only, hold fluids
```

### Warning Alert Example:
```
⚠️ WARNING ALERT - Elevated Sepsis Risk
Patient: Jane Smith (Bed 5)  
Risk Score: 45.2/100
⚠️ INCREASED MONITORING REQUIRED
Please review patient status and vitals closely.
```

## Configuration

1. **Get Bot Token** from @BotFather on Telegram
2. **Get Chat IDs** - Add bot to doctor/nurse chats and use @userinfobot
3. **Update server/.env** with the credentials
4. **Start the bot** and test with buttons

## Testing

1. Add bot to doctor and nurse chats
2. Trigger critical alert from website  
3. Doctor clicks buttons to test workflow
4. Check nurse receives appropriate messages
5. Test `/note` command for rejections

🏥 **Complete doctor-nurse workflow now implemented!**