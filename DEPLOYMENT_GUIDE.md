# 🚀 Deployment Guide - Asclepius AI

## Server Deployment (Render)

### 1. Create Render Web Service
1. Go to [render.com](https://render.com) and connect your GitHub repository
2. Create a new **Web Service** 
3. Set these configurations:

**Build Settings:**
- **Build Command**: `cd server && pip install --upgrade pip setuptools wheel && pip install -r requirements-render.txt`
- **Start Command**: `cd server && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Python Version**: `3.11.9`

**Environment Variables:**
```
MONGODB_URL=mongodb+srv://suryawanshisoham7:Soham1505@linkedin.sgr62ki.mongodb.net/Asclepius?retryWrites=true&w=majority
DATABASE_NAME=Asclepius
TELEGRAM_BOT_TOKEN=8795379419:AAG_fiiluEx-GQI1bHyisFaNuVxzsIMBFo8
TELEGRAM_NURSE_CHAT_ID=-5022062987
TELEGRAM_DOCTOR_CHAT_ID=-5294441613
GEMINI_API_KEY=AIzaSyDoN-5ntP8-zxdhGeO2QBwIaFn3y0LSNMI
DEBUG=false
```

### 2. Deploy
- Click **Create Web Service** 
- Render will automatically build and deploy
- Your API will be available at: `https://your-service-name.onrender.com`

---

## Client Deployment (Vercel)

### 1. Create Vercel Project
1. Go to [vercel.com](https://vercel.com) and connect your GitHub repository
2. Create a new project from your repo
3. Set these configurations:

**Build Settings:**
- **Framework**: Vite
- **Build Command**: `cd client && npm install && npm run build`
- **Output Directory**: `client/dist`
- **Install Command**: `npm install`

**Environment Variables:**
```
VITE_API_URL=https://your-render-service.onrender.com
```

### 2. Deploy
- Click **Deploy**
- Vercel will automatically build and deploy
- Your app will be available at: `https://your-project.vercel.app`

---

## Telegram Bot Setup

### 1. Create Bot with @BotFather
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Choose a name and username for your bot
4. Copy the bot token

### 2. Create Groups and Get Chat IDs
1. Create two Telegram groups:
   - **Nurse ICU Alerts** (for warnings and critical alerts)
   - **Doctor ICU Alerts** (for critical alerts only)
   
2. Add your bot to both groups and make it an admin

3. Get chat IDs using [@userinfobot](https://t.me/userinfobot):
   - Forward a message from each group to @userinfobot
   - It will show the chat ID (negative number for groups)

4. Test the bot by messaging `/test` in the groups

### 3. Update Environment Variables
Update your Render environment variables with:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_NURSE_CHAT_ID=your_nurse_chat_id
TELEGRAM_DOCTOR_CHAT_ID=your_doctor_chat_id
```

---

## Troubleshooting

### Common Render Issues:
- **Build fails**: Check Python version (3.11.9) and requirements-render.txt
- **Import errors**: Ensure all dependencies are listed in requirements-render.txt
- **Memory issues**: Use Free tier limits, optimize code if needed

### Common Vercel Issues:
- **Build fails**: Check Node version and package.json
- **API calls fail**: Verify VITE_API_URL environment variable
- **Routing issues**: Ensure vercel.json rewrites are configured

### Telegram Issues:
- **Bot not responding**: Check bot token and permissions
- **Chat not found**: Verify chat IDs and that bot is admin in groups
- **Messages not sending**: Check internet connectivity and Telegram API status

---

## Live URLs (Current Deployment)
- **Server**: https://ideathon2026-clash-of-code.onrender.com
- **Client**: (Deploy on Vercel to get URL)
- **API Docs**: https://ideathon2026-clash-of-code.onrender.com/docs

---

## Next Steps After Deployment

1. **Test the system**: 
   - Visit your Vercel URL
   - Check if data loads properly
   - Test critical alerts and Telegram notifications

2. **Monitor performance**:
   - Watch Render logs for errors
   - Check Vercel analytics
   - Monitor Telegram bot functionality

3. **Scale if needed**:
   - Upgrade to paid plans if you hit limits
   - Optimize database queries
   - Add error tracking (Sentry, etc.)

🏥 **Your ICU monitoring system is now live!**