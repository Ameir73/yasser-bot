import os
import telebot
import requests
from flask import Flask
from threading import Thread
import time

# 1. إعدادات بوت ياسر (التوكن الجديد الأخير)
TOKEN = "8507472664:AAEUQ5uZWTQtOXtbiBOdxnXLPKz4eFrOvXo"
bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

@server.route("/")
def webhook():
    return "Yasser Bot is Alive!", 200

def run_flask():
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# 2. أمر جلب السعر المباشر (نسخة بينانس المضمونة)
@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        # استلام النص وتنظيفه
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ اكتب اسم العملة، مثال: `/price BTC` ")
            return
            
        coin = parts[1].strip().upper()
        # طلب السعر من بينانس
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            price = float(data['price'])
            # عرض السعر بشكل نظيف جداً
            bot.reply_to(message, f"💰 سعر عملة {coin} الآن:\n${price:,.4f}")
        else:
            bot.reply_to(message, f"❌ عملة {coin} غير موجودة في بينانس حالياً.")
    except Exception as e:
        bot.reply_to(message, "⚠️ السيرفر مشغول قليلاً، حاول مرة أخرى.")

# 3. أمر البداية
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 **تم تفعيل البوت بالتوكن الجديد!**\n\n🎯 الهدف: الزواج من العنود 💍\n📉 جرب الآن: `/price BTC` ")

# 4. التشغيل مع فك التعليق
if __name__ == "__main__":
    # تشغيل خادم الويب
    Thread(target=run_flask).start()
    
    # تنظيف أي جلسة قديمة للتوكن الجديد
    bot.remove_webhook()
    time.sleep(2)
    
    print("--- البوت انطلق بالتوكن الثالث بنجاح ---")
    # تشغيل البوت مع مسح أي رسائل سابقة
    bot.infinity_polling(skip_pending=True)
    
