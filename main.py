import os
import telebot
from telebot import types
import pymongo
from flask import Flask
from threading import Thread
from datetime import datetime

# --- الإعدادات ---
TOKEN = "7948017595:AAFw-ILthgp8F9IopGIqCXlwsqXBRDy4UPY"
MONGO_URI = "mongodb+srv://yasser_user:YasserPass2026@cluster0.mongodb.net/?retryWrites=true&w=majority"
OWNER_ID = 7988144062 

# --- الاتصال بالقاعدة ---
client = pymongo.MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
db = client['YasserQuiz']
q_collection = db['questions']

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
user_data = {}

# --- واجهة لوحة التحكم ---
@bot.message_handler(commands=['start', 'admin'])
def admin_start(message):
    if message.from_user.id != OWNER_ID: return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📂 الأقسام", callback_data="list_secs"))
    markup.add(types.InlineKeyboardButton("➕ إضافة قسم", callback_data="new_sec"))
    bot.send_message(message.chat.id, "💎 **لوحة تحكم ياسر**\nتم إصلاح الكود بالكامل، النظام جاهز.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_hand(call):
    uid = call.from_user.id
    if call.data == "list_secs":
        secs = q_collection.distinct("section")
        markup = types.InlineKeyboardMarkup()
        for s in secs:
            markup.add(types.InlineKeyboardButton(f"📂 {s}", callback_data=f"manage_{s}"))
        bot.edit_message_text("اختر القسم:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("manage_"):
        sec = call.data.split("_")[1]
        count = q_collection.count_documents({"section": sec})
        text = f"📌 قسم: {sec}\n🔢 الأسئلة: {count}\n📅 {datetime.now().strftime('%d/%m/%Y')}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ إضافة سؤال", callback_data=f"addq_{sec}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="list_secs"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("addq_"):
        sec = call.data.split("_")[1]
        user_data[uid] = {"sec": sec}
        msg = bot.send_message(call.message.chat.id, "❓ أرسل السؤال:")
        bot.register_next_step_handler(msg, get_q)

def get_q(message):
    user_data[message.from_user.id]["q"] = message.text
    msg = bot.send_message(message.chat.id, "✅ أرسل الإجابة الصحيحة:")
    bot.register_next_step_handler(msg, get_a)

def get_a(message):
    data = user_data[message.from_user.id]
    q_collection.insert_one({
        "section": data['sec'],
        "q": data['q'],
        "a": message.text,
        "t": 30
    })
    bot.send_message(message.chat.id, "✅ تم حفظ السؤال بنجاح!")
    admin_start(message)

# --- سيرفر التشغيل ---
@server.route('/')
def index(): return "Bot is Running", 200

if __name__ == "__main__":
    Thread(target=lambda: server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))).start()
    bot.infinity_polling()
    
