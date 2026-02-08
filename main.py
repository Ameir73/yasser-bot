import os
import time
from datetime import datetime
from threading import Thread
from flask import Flask
import telebot
from telebot import types
import pymongo

# --- ⚙️ الإعدادات الخاصة بياسر @Ya_79k ---
TOKEN = "7948017595:AAFw-ILthgp8F9IopGIqCXlwsqXBRDy4UPY"

# تم استخدام رابط الاتصال الأكثر استقراراً لتفادي أخطاء DNS في Render
MONGO_URI = "mongodb+srv://yasser_user:YasserPass2026@cluster0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

STORAGE_GROUP_ID = -1003702033956
LOGS_GROUP_ID = -1003712634065
OWNER_ID = 7988144062 

# --- 📦 الاتصال بقاعدة البيانات ---
try:
    # استخدام tlsAllowInvalidCertificates لتجاوز مشاكل شهادات الأمان في السيرفرات المجانية
    client = pymongo.MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=10000)
    db = client['YasserQuiz']
    q_collection = db['questions']
    # اختبار الاتصال
    client.admin.command('ping')
    print("✅ تم الاتصال بنجاح بالسحابة!")
except Exception as e:
    print(f"❌ خطأ اتصال: {e}")

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
user_state = {}

# --- 🖥️ واجهة التحكم الاحترافية ---
def get_section_markup(sec_name):
    q_count = q_collection.count_documents({"section": sec_name})
    today = datetime.now().strftime("%d %B %Y")
    text = (f"📌 قسم: **{sec_name}**\n"
            f"📅 التاريخ: {today}\n"
            f"🔢 عدد الأسئلة: {q_count}\n\n"
            f"اختر من الخدمات التالية:")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ سؤال خيارات", callback_data=f"addopt_{sec_name}"),
        types.InlineKeyboardButton("📝 عرض الأسئلة", callback_data=f"list_{sec_name}"),
        types.InlineKeyboardButton("🗑️ حذف سؤال", callback_data=f"remq_{sec_name}"),
        types.InlineKeyboardButton("⏱️ ضبط وقت القسم", callback_data=f"time_{sec_name}"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="view_secs")
    )
    return text, markup

# --- 📩 الأوامر الرئيسية ---
@bot.message_handler(commands=['admin', 'start'])
def start_cmd(message):
    if message.from_user.id != OWNER_ID: return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📂 أقسامك الخاصة", callback_data="view_secs"))
    markup.add(types.InlineKeyboardButton("➕ إضافة قسم جديد", callback_data="add_new_sec"))
    bot.send_message(message.chat.id, "💎 **مرحباً بك يا مدير ياسر**\nتم إعداد النظام الجديد بالكامل. ابدأ من هنا:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    uid = call.from_user.id
    
    if call.data == "view_secs":
        secs = q_collection.distinct("section")
        markup = types.InlineKeyboardMarkup()
        for s in secs:
            markup.add(types.InlineKeyboardButton(f"📂 {s}", callback_data=f"open_{s}"))
        markup.add(types.InlineKeyboardButton("➕ إضافة قسم", callback_data="add_new_sec"))
        bot.edit_message_text("🗂️ أقسامك الحالية:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("open_"):
        sec = call.data.split("_")[1]
        text, markup = get_section_markup(sec)
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("addopt_"):
        sec = call.data.split("_")[1]
        user_state[uid] = {'sec': sec, 'opts': []}
        msg = bot.send_message(call.message.chat.id, "❓ **أرسل نص السؤال الآن:**")
        bot.register_next_step_handler(msg, step_q)

# --- 🔄 نظام الإضافة المتسلسل (سؤال -> إجابة -> خيارات -> إنهاء) ---
def step_q(message):
    user_state[message.from_user.id]['q'] = message.text
    msg = bot.send_message(message.chat.id, "✅ تم حفظ السؤال. الآن أرسل **الإجابة الصحيحة:**")
    bot.register_next_step_handler(msg, step_ans)

def step_ans(message):
    uid = message.from_user.id
    user_state[uid]['opts'].append(message.text)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ إضافة خيار خاطئ", callback_data="add_extra"))
    markup.add(types.InlineKeyboardButton("➡️ الانتقال لكتابة السؤال التالي", callback_data="next_q_save"))
    markup.add(types.InlineKeyboardButton("⏱️ ضبط الوقت وإنهاء القسم", callback_data="finish_setup"))
    bot.send_message(message.chat.id, f"🌟 تم حفظ الإجابة: ({message.text})\nماذا تريد أن تفعل الآن؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["add_extra", "next_q_save", "finish_setup"])
def handle_steps(call):
    uid = call.from_user.id
    if call.data == "add_extra":
        msg = bot.send_message(call.message.chat.id, "أرسل الخيار الإضافي:")
        bot.register_next_step_handler(msg, step_wrong)
    
    elif call.data == "next_q_save":
        save_to_db(uid) # حفظ السؤال الحالي
        sec = user_state[uid]['sec']
        user_state[uid] = {'sec': sec, 'opts': []} # تصفير البيانات لسؤال جديد
        msg = bot.send_message(call.message.chat.id, "📝 **أرسل نص السؤال التالي:**")
        bot.register_next_step_handler(msg, step_q)

    elif call.data == "finish_setup":
        save_to_db(uid)
        sec = user_state[uid]['sec']
        markup = types.InlineKeyboardMarkup()
        for t in [15, 30, 60]:
            markup.add(types.InlineKeyboardButton(f"{t} ثانية", callback_data=f"settime_{sec}_{t}"))
        bot.edit_message_text(f"⏱️ اختر الوقت لجميع أسئلة قسم {sec}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

def step_wrong(message):
    user_state[message.from_user.id]['opts'].append(message.text)
    bot.send_message(message.chat.id, f"✅ تمت إضافة الخيار الخاطئ: {message.text}")
    step_ans(message) # العودة للأزرار

def save_to_db(uid):
    data = user_state.get(uid)
    if data and 'q' in data:
        q_doc = {
            "section": data['sec'],
            "q": data['q'],
            "a": data['opts'][0],
            "options": data['opts'],
            "t": 30 # وقت افتراضي
        }
        q_collection.insert_one(q_doc)
        bot.send_message(STORAGE_GROUP_ID, f"📦 تخزين سؤال جديد في قسم {data['sec']}")
        bot.send_message(LOGS_GROUP_ID, f"📑 سجل: أضاف المشرف سؤالاً جديداً.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("settime_"))
def finalize_time(call):
    _, sec, t = call.data.split("_")
    q_collection.update_many({"section": sec}, {"$set": {"t": int(t)}})
    bot.answer_callback_query(call.id, "✅ تم ضبط الوقت لجميع الأسئلة!")
    text, markup = get_section_markup(sec)
    bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# --- 🌐 السيرفر والتشغيل ---
@server.route("/")
def home(): return "Yasser Bot LIVE", 200

if __name__ == "__main__":
    Thread(target=lambda: server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))).start()
    bot.infinity_polling(skip_pending=True)
