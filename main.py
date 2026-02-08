import os
import telebot
import requests
from flask import Flask
from threading import Thread
import time

# 1. إعدادات بوت ياسر 
TOKEN = "8507472664:AAFPkBX-w0nns4A8uk1cSf8tIfdyVCShW0A"
bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

@server.route("/")
def webhook():
    return "Bot is Active!", 200

def run_flask():
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# 2. أمر جلب السعر (تنظيف كامل للاسم)
@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ اكتب اسم العملة، مثال: `/price BTC` ")
            return
            
        # تنظيف اسم العملة من أي فراغات أو رموز
        coin = parts[1].strip().upper()
        
        # رابط بينانس المباشر
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price = float(data['price'])
            # عرض السعر بدون نجوم في البداية لضمان العمل
            bot.reply_to(message, f"💰 سعر {coin} الآن هو:\n${price:,.4f}")
        else:
            bot.reply_to(message, f"❌ عملة {coin} غير موجودة في بينانس.\nتأكد من كتابة الرمز فقط (مثل BTC).")
    except Exception:
        bot.reply_to(message, "⚠️ السيرفر مشغول، حاول ثانية.")

# 3. أمر البداية
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 بوت ياسر متصل!\n\nجرب الآن: `/price BTC` ")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.remove_webhook()
    time.sleep(1)
    print("البوت انطلق!")
    bot.infinity_polling(skip_pending=True)
            
