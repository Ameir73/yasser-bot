import os
import telebot
import requests
from flask import Flask
from threading import Thread
import time

# 1. إعدادات بوت ياسر (التوكن الجديد)
TOKEN = "8507472664:AAFPkBX-w0nns4A8uk1cSf8tIfdyVCShW0A"
bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

@server.route("/")
def webhook():
    return "Yasser Bot is Active with New Token!", 200

def run_flask():
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# 2. أمر جلب السعر المباشر
@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ اكتب اسم العملة، مثال: `/price BTC` ")
            return
            
        coin = parts[1].upper().strip()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'price' in data:
            price = float(data['price'])
            bot.reply_to(message, f"💰 سعر **{coin}** الآن:\n`${price:,.4f}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ عملة **{coin}** غير موجودة في بينانس.")
    except Exception:
        bot.reply_to(message, "⚠️ حاول مرة أخرى.")

# 3. أمر البداية مع هدفك الشخصي
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "🚀 **أهلاً بك في بوت ياسر للتداول!**\n\n"
        "🎯 **الهدف:** الزواج من العنود 💍\n"
        "📈 **الأوامر:**\n"
        "🔹 `/price BTC` جلب السعر\n"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# 4. التشغيل
if __name__ == "__main__":
    Thread(target=run_flask).start()
    
    # تنظيف أي اتصال قديم بالتوكن الجديد
    bot.remove_webhook()
    time.sleep(1)
    
    print("--- البوت انطلق بالتوكن الجديد يا ياسر ---")
    bot.infinity_polling(skip_pending=True)
