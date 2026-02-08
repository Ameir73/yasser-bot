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
    return "Yasser Bot is Active!", 200

def run_flask():
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# 2. أمر جلب السعر المطور
@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        # تقسيم الرسالة لأخذ الكلمة الثانية فقط (اسم العملة)
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ يرجى كتابة اسم العملة بعد الأمر.\nمثال: `/price BTC`", parse_mode="Markdown")
            return
        
        coin = parts[1].upper() # تحويل الحروف لكبيرة
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT"
        res = requests.get(url).json()
        
        if 'price' in res:
            price = float(res['price'])
            bot.reply_to(message, f"💰 سعر عملة **{coin}** الآن:\n`${price:.4f}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ عملة **{coin}** غير مدعومة أو غير موجودة في بينانس.", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "⚠️ حدث خطأ، تأكد من كتابة اسم العملة بشكل صحيح.")

# 3. التشغيل مع تنظيف الاتصالات القديمة
if __name__ == "__main__":
    Thread(target=run_flask).start()
    # حذف الـ Webhook القديم فوراً لحل مشكلة Conflict 409
    bot.remove_webhook()
    time.sleep(1)
    print("--- البوت انطلق بنجاح يا ياسر ---")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
        
