#!/bin/bash

echo "🚀 Asclepius AI - Quick Telegram Setup"
echo "===================================="

echo ""
echo "📱 Step 1: Create Telegram Bot"
echo "1. Message @BotFather in Telegram"
echo "2. Send: /newbot"  
echo "3. Name: Asclepius ICU Bot"
echo "4. Username: asclepius_icu_bot (or similar)"
echo "5. Copy the token"

echo ""
read -p "Enter your bot token: " BOT_TOKEN

echo ""
echo "📋 Step 2: Get Chat ID"
echo "1. Start chat with your bot or add it to a group"
echo "2. Send a message"
echo "3. Visit: https://api.telegram.org/bot${BOT_TOKEN}/getUpdates"
echo "4. Find 'chat' -> 'id' (for groups, it's negative)"

echo ""
read -p "Enter nurse chat ID: " NURSE_CHAT
read -p "Enter doctor chat ID (can be same): " DOCTOR_CHAT

echo ""
echo "🧪 Testing configuration..."
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d "chat_id=${NURSE_CHAT}" \
  -d "text=🧪 Test from Asclepius AI setup script!" \
  -d "parse_mode=HTML"

if [ $? -eq 0 ]; then
  echo "✅ Test message sent!"
else
  echo "❌ Test failed - check your token and chat ID"
fi

echo ""
echo "🔧 Add these to your Render environment variables:"
echo "TELEGRAM_BOT_TOKEN = ${BOT_TOKEN}"
echo "TELEGRAM_NURSE_CHAT_ID = ${NURSE_CHAT}" 
echo "TELEGRAM_DOCTOR_CHAT_ID = ${DOCTOR_CHAT}"

echo ""
echo "Then redeploy your service and test with:"
echo "https://ideathon2026-clash-of-code.onrender.com/telegram/test"