import os
import telebot
import requests
from flask import Flask
from threading import Thread

# 1. إعدادات بوت ياسر
TOKEN = "8507472664:AAGQ_xlh-CLwCafVBGp5YPaBOmD_th4Oq88"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@server.route("/")
def webhook():
    return "Yasser Bot is Running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)

# 2. الأوامر
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ **بوت ياسر جاهز للعمل!**\n\nأرسل اسم العملة بهذا الشكل:\n`/price BTC`", parse_mode="Markdown")

@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        # تحسين قراءة النص لتجنب الأخطاء
        text_parts = message.text.split()
        if len(text_parts) < 2:
            bot.reply_to(message, "❌ يرجى كتابة اسم العملة.\nمثال: `/price FET`", parse_mode="Markdown")
            return
            
        coin = text_parts[1].upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT"
        res = requests.get(url).json()
        
        if 'price' in res:
            price = float(res['price'])
            bot.reply_to(message, f"💰 سعر **{coin}** الآن:\n`${price:.4f}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ لم أجد عملة باسم {coin} في بينانس.")
    except Exception as e:
        bot.reply_to(message, "⚠️ حدث خطأ أثناء جلب السعر.")

# 3. التشغيل
if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("Bot is starting...")
    bot.infinity_polling()
