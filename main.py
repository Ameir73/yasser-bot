from pyrogram import Client, filters
import json
from urllib.request import urlopen
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- 1. إعدادات البوت (بياناتك) ---
api_id = 21437281
api_hash = "6d8fd92d56b9b9db9377cc493fa641d0"
bot_token = "8507472664:AAGQ_xlh-CLwCafVBGp5YPaBOmD_th4Oq88"

# --- 2. حل مشكلة Render (خادم وهمي) ---
def run_dummy_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is Running Safely!")
    server = HTTPServer(('0.0.0.0', 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 3. تشغيل البوت ---
app = Client("yasser_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# --- 4. أمر البداية والمعلومات ---
@app.on_message(filters.command("start"))
async def start(client, message):
    info_text = (
        "👋 **أهلاً بك في بوت التداول الاحترافي!**\n\n"
        "👤 **المطور:** ياسر\n"
        "🎯 **الهدف:** تحقيق الأهداف والزواج من العنود 💍\n"
        "🛡️ **الاستراتيجية:** انفجار السيولة وقنص الارتدادات\n\n"
        "🚀 **الأوامر المتاحة:**\n"
        "🔹 `/price [العملة]` - لسعر العملة المباشر\n"
        "🔹 `/long [العملة] [السعر]` - توصية شراء\n"
        "🔹 `/short [العملة] [السعر]` - توصية بيع"
    )
    await message.reply_text(info_text, disable_web_page_preview=True)

# --- 5. أمر جلب السعر المباشر ---
@app.on_message(filters.command("price"))
async def get_price(client, message):
    try:
        coin = message.command[1].upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT"
        response = urlopen(url)
        data = json.loads(response.read())
        price = float(data['price'])
        await message.reply_text(f"💰 سعر عملة **{coin}** الآن هو: `${price:.4f}`")
    except:
        await message.reply_text("❌ اكتب اسم العملة فقط، مثال: `/price BTC`")

# --- 6. أمر صفقات الشراء (Long) ---
@app.on_message(filters.command("long"))
async def long_trade(client, message):
    try:
        coin = message.command[1].upper()
        entry = float(message.command[2])
        msg = (
            f"🔥 فرصة انفجار سعري: #{coin}USDT 🚀\n\n"
            f"🎯 منطقة الدخول: {entry:.4f}\n"
            f"💰 أهداف الربح:\n"
            f"1️⃣ {entry*1.02:.4f} ⚡\n"
            f"2️⃣ {entry*1.05:.4f} 🚀\n"
            f"3️⃣ {entry*1.08:.4f} 🚀🚀\n\n"
            f"🛡️ تعزيز (DCA): {entry*0.97:.4f}\n"
            f"🚫 وقف الخسارة: {entry*0.95:.4f}\n\n"
            f"القرار: دخول قوي (Long) بناءً على استراتيجية انفجار السيولة."
        )
        await message.reply_text(msg)
    except:
        await message.reply_text("مثال: `/long FET 0.2855`")

# --- 7. أمر صفقات البيع (Short) ---
@app.on_message(filters.command("short"))
async def short_trade(client, message):
    try:
        coin = message.command[1].upper()
        entry = float(message.command[2])
        msg = (
            f"📉 فرصة هبوط (Short): #{coin}USDT\n\n"
            f"🎯 منطقة الدخول: {entry:.4f}\n"
            f"💰 أهداف الهبوط:\n"
            f"1️⃣ {entry*0.98:.4f} ⚡\n"
            f"2️⃣ {entry*0.95:.4f} 🚀\n"
            f"3️⃣ {entry*0.92:.4f} 🚀🚀\n\n"
            f"🚫 وقف الخسارة: {entry*1.05:.4f}\n\n"
            f"القرار: بيع (Short) بناءً على استراتيجية قنص الارتدادات."
        )
        await message.reply_text(msg)
    except:
        await message.reply_text("مثال: `/short BTC 50000`")

print("البوت الاحترافي انطلق!")
app.run()
    
