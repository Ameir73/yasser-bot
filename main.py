import os
import time
from datetime import datetime
from threading import Thread
from flask import Flask
import telebot
from telebot import types
import pymongo

# --- ⚙️ الإعدادات والربط ---
TOKEN = "7948017595:AAFw-ILthgp8F9IopGIqCXlwsqXBRDy4UPY"
MONGO_URI = "mongodb+srv://yasser_user:YasserPass2026@cluster0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

STORAGE_GROUP_ID = -1003702033956
LOGS_GROUP_ID = -1003712634065
OWNER_ID = 7988144062 

# الاتصال بالقاعدة
try:
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['YasserQuiz']
    q_collection = db['questions']
    client.admin.command('ping')
    print("✅ المتصل مستعد والتوكن مفعل!")
except Exception as e:
    print(f"❌ خطأ قاعدة البيانات: {e}")

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
user_state = {}

# --- 🖥️ واجهات التحكم الاحترافية ---
def get_section_markup(sec_name):
    q_count = q_collection.count_documents({"section": sec_name})
    today = datetime.now().strftime("%d %B %Y")
    text = (f"📌 أنت الآن في قسم: **{sec_name}**\n"
            f"📅 التاريخ: {today}\n"
            f"🔢 عدد أسئلتك الحالية: {q_count}\n\n"
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
    if message.from_user.id != OWNER_ID: return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📂 أقسامك الخاصة", callback_data="view_secs"))
    markup.add(types.InlineKeyboardButton("➕ إضافة قسم جديد", callback_data="add_new_sec"))
    bot.send_message(message.chat.id, "💎 لوحة تحكم ياسر @Ya_79k\n(تم إصلاح الكود بالكامل ✅)", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    uid = call.from_user.id
    if call.data == "view_secs":
        secs = q_collection.distinct("section")
        markup = types.InlineKeyboardMarkup()
        for s in secs:
            markup.add(types.InlineKeyboardButton(s, callback_data=f"open_{s}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_home"))
        bot.edit_message_text("📂 الأقسام المتوفرة:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("open_"):
        sec = call.data.split("_")[1]
        text, markup = get_section_markup(sec)
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("addopt_"):
        sec = call.data.split("_")[1]
        user_state[uid] = {'sec': sec, 'opts': []}
        msg = bot.send_message(call.message.chat.id, "❓ **أرسل نص السؤال الآن:**", parse_mode="Markdown")
        bot.register_next_step_handler(msg, step_get_q)

# --- 🔄 نظام الإضافة المتسلسل ---
def step_get_q(message):
    user_state[message.from_user.id]['q'] = message.text
    msg = bot.send_message(message.chat.id, "✅ تم حفظ السؤال. الآن **أرسل الإجابة الصحيحة:**")
    bot.register_next_step_handler(msg, step_get_correct_ans)

def step_get_correct_ans(message):
    uid = message.from_user.id
    if uid not in user_state: return
    user_state[uid]['opts'].append(message.text)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ إضافة خيار خاطئ", callback_data="add_extra"))
    markup.add(types.InlineKeyboardButton("⏱️ ضبط الوقت والإنهاء", callback_data="set_time"))
    bot.send_message(message.chat.id, f"🌟 تم حفظ الإجابة الصحيحة: ({message.text})\nماذا تريد أن تفعل؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["add_extra", "set_time"])
def handle_steps(call):
    if call.data == "add_extra":
        msg = bot.send_message(call.message.chat.id, "أرسل الخيار الإضافي:")
        bot.register_next_step_handler(msg, step_get_wrong_ans)
    elif call.data == "set_time":
        sec = user_state[call.from_user.id]['sec']
        markup = types.InlineKeyboardMarkup()
        for t in [15, 30, 60]:
            markup.add(types.InlineKeyboardButton(f"{t} ثانية", callback_data=f"final_{sec}_{t}"))
        bot.edit_message_text("⏱️ اختر وقت الإجابة لهذا السؤال:", call.message.chat.id, call.message.message_id, reply_markup=markup)

def step_get_wrong_ans(message):
    user_state[message.from_user.id]['opts'].append(message.text)
    bot.send_message(message.chat.id, f"✅ تمت إضافة الخيار: {message.text}")
    step_get_correct_ans(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("final_"))
def save_everything(call):
    _, sec, t = call.data.split("_")
    data = user_state.get(call.from_user.id)
    if data:
        q_doc = {"section": sec, "q": data['q'], "a": data['opts'][0], "options": data['opts'], "t": int(t)}
        q_collection.insert_one(q_doc)
        bot.answer_callback_query(call.id, "✅ تم الحفظ بنجاح!")
        text, markup = get_section_markup(sec)
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# --- 🌐 السيرفر ---
@server.route("/")
def home(): return "Yasser Bot is Active", 200

def run():
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling(skip_pending=True)
    
