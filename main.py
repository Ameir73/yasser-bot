import os
import telebot
from telebot import types
import pymongo
from flask import Flask
from threading import Thread
import time

# --- إعدادات الاتصال الجديدة لياسر ---
TOKEN = "7948017595:AAFpATTA4rHa5ED3N9d_gYbPgeOWIGdNqH8"
# رابط قاعدة البيانات السحابية الجاهز
MONGO_URI = "mongodb+srv://yasser_user:YasserPass2026@cluster0.mongodb.net/YasserQuiz?retryWrites=true&w=majority"

# الاتصال بقاعدة البيانات
client = pymongo.MongoClient(MONGO_URI)
db = client['YasserQuiz']
q_collection = db['questions']
admin_collection = db['admins']
score_collection = db['scores']

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# ID حسابك الجديد ليتم التعرف عليك كمدير عام
OWNER_ID = 7988144062 

def is_admin(user_id):
    if user_id == OWNER_ID: return True
    return admin_collection.find_one({"user_id": user_id}) is not None

# --- لوحة التحكم ---
@bot.message_handler(commands=['admin', 'لوحة_التحكم'])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "❌ هذه اللوحة مخصصة للمدير @Ya_79k فقط.")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ إضافة سؤال", callback_data="add_q"),
        types.InlineKeyboardButton("📂 الأقسام والبدء", callback_data="view_secs"),
        types.InlineKeyboardButton("📊 الترتيب العام", callback_data="show_rank"),
        types.InlineKeyboardButton("👤 رفع مشرف", callback_data="add_adm")
    )
    bot.reply_to(message, "⚙️ **لوحة التحكم السحابية**\nمرحباً بك يا مدير ياسر، كل شيء جاهز للانطلاق!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    if not is_admin(call.from_user.id): return

    if call.data == "add_q":
        msg = bot.send_message(call.message.chat.id, "📝 أرسل السؤال بالتنسيق:\nالقسم - السؤال - الإجابة - الوقت")
        bot.register_next_step_handler(msg, save_q_to_db)
    
    elif call.data == "view_secs":
        secs = q_collection.distinct("section")
        if not secs:
            bot.answer_callback_query(call.id, "⚠️ لا توجد أسئلة حالياً!")
            return
        markup = types.InlineKeyboardMarkup()
        for s in secs:
            markup.add(types.InlineKeyboardButton(f"🏁 ابدأ: {s}", callback_data=f"start_{s}"))
        bot.edit_message_text("اختر القسم لبدء التحدي:", call.message.chat.id, call.message.message_id, reply_markup=markup)

def save_q_to_db(message):
    try:
        parts = message.text.split("-")
        q_collection.insert_one({
            "section": parts[0].strip(),
            "q": parts[1].strip(),
            "a": parts[2].strip(),
            "t": int(parts[3].strip())
        })
        bot.reply_to(message, "✅ تم الحفظ في قاعدة البيانات!")
    except:
        bot.reply_to(message, "❌ خطأ! التنسيق: قسم - سؤال - جواب - وقت")

# --- خادم الويب لـ Render ---
@server.route("/")
def home(): return "Yasser Pro Bot is Online!", 200

def run_flask():
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.remove_webhook()
    time.sleep(1)
    print("--- البوت انطلق بالتوكن الجديد يا ياسر ---")
    bot.infinity_polling(skip_pending=True)
        
