import os
import telebot
import requests
from flask import Flask
from threading import Thread

# 1. إعدادات البوت
TOKEN = "8507472664:AAGQ_xlh-CLwCafVBGp5YPaBOmD_th4Oq88"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# 2. نظام النبض لإرضاء Render
@server.route("/")
def webhook():
    return "Bot is Alive!", 200

def run_flask():
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# 3. الأوامر (سعر العملة)
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 أهلاً يا ياسر! البوت شغال الآن بنظام Telebot المستقر.\n\nجرب أرسل: `/price BTC`", parse_mode="Markdown")

@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        coin = message.text.split()[1].upper()
        res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT").json()
        price = float(res['price'])
        bot.reply_to(message, f"💰 سعر **{coin}** الآن: `${price:.4f}`", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ اكتب العملة صح، مثال: `/price BTC`")

# 4. تشغيل كل شيء
if __name__ == "__main__":
    # تشغيل Flask في الخلفية
    Thread(target=run_flask).start()
    print("--- البوت انطلق بنجاح يا ياسر ---")
    # تشغيل البوت
    bot.infinity_polling()
    
