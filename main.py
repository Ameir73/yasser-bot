import os
import telebot
import requests
from flask import Flask
from threading import Thread
import time

# 1. إعدادات بوت ياسر
TOKEN = "8507472664:AAGQ_xlh-CLwCafVBGp5YPaBOmD_th4Oq88"
bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

@server.route("/")
def webhook():
    return "Yasser Bot is 100% Active!", 200

def run_flask():
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# 2. الأوامر المحسنة
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ **أهلاً ياسر! البوت جاهز تماماً.**\nأرسل الآن: `/price BTC` جربها!")

@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        # قراءة اسم العملة فقط وتجاهل الأمر
        text = message.text.strip().split()
        if len(text) < 2:
            bot.reply_to(message, "❌ اكتب اسم العملة، مثال: `/price FET` ")
            return
            
        coin = text[1].upper()
        # جلب السعر من بينانس
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT"
        res = requests.get(url).json()
        
        if 'price' in res:
            price = float(res['price'])
            # عرض السعر بشكل جميل
            bot.reply_to(message, f"💰 سعر **{coin}** الآن:\n`${price:.4f}`")
        else:
            bot.reply_to(message, f"❌ عملة {coin} غير موجودة في بينانس.")
    except Exception as e:
        bot.reply_to(message, "⚠️ حاول مرة أخرى.")

# 3. التشغيل مع تفادي التعارض
if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("--- جارِ تشغيل البوت بنجاح ---")
    # حذف الـ Webhook القديم لفك التعليق
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    
