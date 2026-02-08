import os
import telebot
from telebot import types
import pymongo
from flask import Flask
from threading import Thread
import time
from datetime import datetime

# --- الإعدادات ---
TOKEN = "7948017595:AAFpATTA4rHa5ED3N9d_gYbPgeOWIGdNqH8"
MONGO_URI = "mongodb+srv://yasser_user:YasserPass2026@cluster0.mongodb.net/YasserQuiz?retryWrites=true&w=majority"
STORAGE_GROUP_ID = -1003702033956
LOGS_GROUP_ID = -1003712634065
OWNER_ID = 7988144062 

client = pymongo.MongoClient(MONGO_URI)
db = client['YasserQuiz']
q_collection = db['questions']
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# تخزين مؤقت لإدارة الجلسات
user_state = {}

# --- لوحة التحكم الرئيسية ---
@bot.message_handler(commands=['admin', 'start'])
def main_panel(message):
    if message.from_user.id != OWNER_ID: return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("أقسامك الخاصة", callback_data="view_secs"),
        types.InlineKeyboardButton("إضافة قسم", callback_data="add_new_sec"),
        types.InlineKeyboardButton("إغلاق", callback_data="close")
    )
    bot.send_message(message.chat.id, "أهلاً بك يا ياسر! قم بتهيئة المسابقة:", reply_markup=markup)

# --- واجهة إدارة القسم (مثل الصورة) ---
def get_section_interface(sec_name):
    q_count = q_collection.count_documents({"section": sec_name})
    today = datetime.now().strftime("%d %B %Y")
    
    text = (f"📍 {today}\n"
            f"📌 أنت الآن في قسم: **{sec_name}**\n"
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

@bot.callback_query_handler(func=lambda call: True)
def handle_all_clicks(call):
    user_id = call.from_user.id
    
    if call.data == "view_secs":
        secs = q_collection.distinct("section")
        markup = types.InlineKeyboardMarkup()
        for s in secs:
            markup.add(types.InlineKeyboardButton(s, callback_data=f"open_{s}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_home"))
        bot.edit_message_text("📂 اختر القسم المراد إدارته:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("open_"):
        sec = call.data.split("_")[1]
        text, markup = get_section_interface(sec)
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # --- مسار إضافة سؤال بخيارات (طلبك الجديد) ---
    elif call.data.startswith("addopt_"):
        sec = call.data.split("_")[1]
        user_state[user_id] = {'sec': sec, 'step': 'Q', 'options': []}
        msg = bot.send_message(call.message.chat.id, "❓ أرسل نص السؤال:")
        bot.register_next_step_handler(msg, process_opt_q)

def process_opt_q(message):
    user_id = message.from_user.id
    user_state[user_id]['q_text'] = message.text
    msg = bot.send_message(message.chat.id, "✅ تم حفظ السؤال. الآن **أرسل الإجابة الصحيحة**:")
    bot.register_next_step_handler(msg, process_correct_ans)

def process_correct_ans(message):
    user_id = message.from_user.id
    user_state[user_id]['options'].append(message.text) # أول إجابة هي الصحيحة
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ إضافة خيار خاطئ", callback_data="add_wrong"))
    markup.add(types.InlineKeyboardButton("⏱️ ضبط الوقت والإنهاء", callback_data="finish_q"))
    
    bot.send_message(message.chat.id, "🌟 تم حفظ الإجابة الصحيحة. هل تريد إضافة خيارات أخرى؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["add_wrong", "finish_q"])
def manage_options(call):
    user_id = call.from_user.id
    if call.data == "add_wrong":
        msg = bot.send_message(call.message.chat.id, "أرسل الخيار الخاطئ:")
        bot.register_next_step_handler(msg, save_wrong_opt)
    elif call.data == "finish_q":
        show_time_options(call)

def save_wrong_opt(message):
    user_id = message.from_user.id
    user_state[user_id]['options'].append(message.text)
    bot.send_message(message.chat.id, f"✅ تمت إضافة الخيار: {message.text}")
    process_correct_ans(message) # إعادة إظهار الأزرار

def show_time_options(call):
    sec = user_state[call.from_user.id]['sec']
    markup = types.InlineKeyboardMarkup()
    for t in [15, 30, 60]:
        markup.add(types.InlineKeyboardButton(f"{t} ثانية", callback_data=f"sv_{sec}_{t}"))
    bot.edit_message_text("⏱️ حدد وقت الإجابة لهذا القسم:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sv_"))
def final_save(call):
    _, sec, t = call.data.split("_")
    data = user_state[call.from_user.id]
    
    q_doc = {
        "section": sec,
        "q": data['q_text'],
        "a": data['options'][0],
        "options": data['options'],
        "t": int(t)
    }
    q_collection.insert_one(q_doc)
    bot.send_message(STORAGE_GROUP_ID, f"📦 تم تخزين سؤال خيارات في {sec}")
    bot.answer_callback_query(call.id, "✅ تم الحفظ بنجاح!")
    
    # العودة لواجهة القسم
    text, markup = get_section_interface(sec)
    bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# --- خادم الويب ---
@server.route("/")
def home(): return "Yasser Pro Bot LIVE", 200

if __name__ == "__main__":
    Thread(target=lambda: server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))).start()
    bot.infinity_polling(skip_pending=True)
    
