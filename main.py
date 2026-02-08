import os
import time
from datetime import datetime
from threading import Thread
from flask import Flask
import telebot
from telebot import types
import pymongo # تأكد من وجود pymongo[srv] في ملف requirements.txt

# --- ⚙️ الإعدادات (التوكن الجديد) ---
TOKEN = "7948017595:AAFw-ILthgp8F9IopGIqCXlwsqXBRDy4UPY"
# الرابط المحدث لضمان استقرار الاتصال
MONGO_URI = "mongodb+srv://yasser_user:YasserPass2026@cluster0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

STORAGE_GROUP_ID = -1003702033956
LOGS_GROUP_ID = -1003712634065
OWNER_ID = 7988144062 

# --- 📦 نظام الاتصال الذكي ---
try:
    # إضافة tlsAllowInvalidCertificates لتفادي مشاكل الحماية في السيرفرات المجانية
    client = pymongo.MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
    db = client['YasserQuiz']
    q_collection = db['questions']
    client.admin.command('ping')
    print("✅ تم الاتصال بقاعدة البيانات بنجاح!")
except Exception as e:
    print(f"❌ خطأ فادح في قاعدة البيانات: {e}")

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
user_state = {}

# --- 🖥️ واجهات التحكم الاحترافية ---
def get_section_markup(sec_name):
    try:
        q_count = q_collection.count_documents({"section": sec_name})
    except:
        q_count = "خطأ في الاتصال"
    
    today = datetime.now().strftime("%d %B %Y")
    text = (f"📌 قسم: **{sec_name}**\n"
            f"📅 التاريخ: {today}\n"
            f"🔢 الأسئلة الحالية: {q_count}\n\n"
            f"اختر من الخدمات التالية:")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("تغيير اسم القسم", callback_data=f"rename_{sec_name}"),
        types.InlineKeyboardButton("حذف القسم", callback_data=f"delsec_{sec_name}"),
        types.InlineKeyboardButton("+سؤال مباشر", callback_data=f"addq_{sec_name}"),
        types.InlineKeyboardButton("+سؤال خيارات", callback_data=f"addopt_{sec_name}"),
        types.InlineKeyboardButton("تعديل سؤال", callback_data=f"editq_{sec_name}"),
        types.InlineKeyboardButton("حذف سؤال", callback_data=f"remq_{sec_name}"),
        types.InlineKeyboardButton("عرض الأسئلة", callback_data=f"list_{sec_name}"),
        types.InlineKeyboardButton("رجوع", callback_data="view_secs")
    )
    return text, markup

# --- 📩 معالجة الأوامر ---
@bot.message_handler(commands=['admin', 'start'])
def start_cmd(message):
    if message.from_user.id != OWNER_ID:
        return bot.reply_to(message, "❌ الوصول للمدير فقط.")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📂 أقسامك الخاصة", callback_data="view_secs"))
    markup.add(types.InlineKeyboardButton("➕ إضافة قسم جديد", callback_data="add_new_sec"))
    bot.send_message(message.chat.id, "💎 **أهلاً بك يا ياسر في لوحة التحكم**\nتم تحديث الاتصال والنظام جاهز الآن.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    uid = call.from_user.id
    if call.data == "view_secs":
        try:
            secs = q_collection.distinct("section")
            markup = types.InlineKeyboardMarkup()
            for s in secs:
                markup.add(types.InlineKeyboardButton(s, callback_data=f"open_{s}"))
            markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_home"))
            bot.edit_message_text("📂 الأقسام المتوفرة:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            bot.answer_callback_query(call.id, "❌ خطأ: تعذر الوصول لقاعدة البيانات.")

    elif call.data.startswith("open_"):
        sec = call.data.split("_")[1]
        text, markup = get_section_markup(sec)
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# --- 🌐 خادم الويب ---
@server.route("/")
def home(): return "Yasser Bot is Active", 200

def run():
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling(skip_pending=True)
    
