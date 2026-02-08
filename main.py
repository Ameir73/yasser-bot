import os
import json
import threading
from urllib.request import urlopen
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters

# --- 1. بياناتك ---
API_ID = 21437281
API_HASH = "6d8fd92d56b9b9db9377cc493fa641d0"
BOT_TOKEN = "8507472664:AAGQ_xlh-CLwCafVBGp5YPaBOmD_th4Oq88"

# --- 2. خدعة المنفذ لـ Render (إلزامي) ---
def run_port_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Yasser Bot is Alive!")
    # Render يعطي منفذ عشوائي عبر المتغير PORT، وإذا لم يوجد نستخدم 10000
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

threading.Thread(target=run_port_server, daemon=True).start()

# --- 3. إعداد البوت ---
app = Client("yasser_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("🚀 بوت ياسر الاحترافي متصل الآن!\n\nجرب أمر السعر:\n`/price BTC`", parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.command("price"))
async def get_price(client, message):
    try:
        symbol = message.command[1].upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        with urlopen(url) as response:
            data = json.loads(response.read())
            price = float(data['price'])
            await message.reply_text(f"💰 سعر **{symbol}** الآن:\n`${price:.4f}`")
    except Exception:
        await message.reply_text("❌ خطأ! اكتب العملة صح (مثال: `/price BTC`)")

# تشغيل البوت
print("--- البوت بدأ العمل ---")
app.run()
