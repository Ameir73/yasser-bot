import os
import time
from datetime import datetime
from threading import Thread
from flask import Flask
import telebot
from telebot import types
import pymongo

# --- ⚙️ إعدادات ياسر النهائية ---
TOKEN = "7948017595:AAFw-ILthgp8F9IopGIqCXlwsqXBRDy4UPY"
# تم تغيير الرابط للرابط المباشر (بدون srv) لحل مشكلة DNS في Render
MONGO_URI = "mongodb://yasser_user:YasserPass2026@cluster0-shard-00-00.mongodb.net:27017,cluster0-shard-00-01.mongodb.net:27017,cluster0-shard-00-02.mongodb.net:27017/YasserQuiz?ssl=true&replicaSet=atlas-xxxxx-shard-0&authSource=admin&retryWrites=true&w=majority"

# ملاحظة: إذا لم يعمل الرابط أعلاه، استخدم هذا الرابط المبسط جداً:
# MONGO_URI = "mongodb://yasser_user:YasserPass2026@cluster0.mongodb.net:27017/YasserQuiz?authSource=admin"

OWNER_ID = 7988144062 

# --- 📦 محاولة الاتصال ---
try:
    # استخدام الاتصال المباشر وتجاهل فحص الشهادات الزائد
    client = pymongo.MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=10000)
    db = client['YasserQuiz']
    q_collection = db['questions']
    # اختبار الاتصال الفعلي
    client.admin.command('ping')
    print("✅ تم الاتصال المباشر بنجاح يا ياسر!")
except Exception as e:
    print(f"❌ خطأ الاتصال المستمر: {e}")

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# --- 🖥️ الواجهات ---
@bot.message_handler(commands=['admin', 'start'])
def start_cmd(message):
    if message.from_user.id != OWNER_ID: return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📂 أقسامك الخاصة", callback_data="view_secs"))
    markup.add(types.InlineKeyboardButton("➕ إضافة قسم جديد", callback_data="add_new_sec"))
    bot.send_message(message.chat.id, "💎 **تم تحديث الاتصال بالنظام المباشر**\nجرب الضغط على الأزرار الآن.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    if call.data == "view_secs":
        try:
            secs = q_collection.distinct("section")
            markup = types.InlineKeyboardMarkup()
            for s in secs:
                markup.add(types.InlineKeyboardButton(s, callback_data=f"open_{s}"))
            markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
            bot.edit_message_text("📂 أقسامك الحالية:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        except Exception as e:
            bot.answer_callback_query(call.id, "⚠️ القاعدة لا تزال لا تستجيب.. تأكد من Network Access")

# --- 🌐 السيرفر ---
@server.route("/")
def home(): return "Yasser Bot LIVE", 200

if __name__ == "__main__":
    Thread(target=lambda: server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))).start()
    bot.infinity_polling(skip_pending=True)
        
