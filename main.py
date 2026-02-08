import os
import json
import threading
from urllib.request import urlopen
from flask import Flask
from pyrogram import Client, filters

# --- 1. إعداد الخادم (عشان Render يرضى علينا) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Running!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# تشغيل الخادم في خيط منفصل
threading.Thread(target=run_web_server, daemon=True).start()

# --- 2. إعدادات بوت ياسر ---
API_ID = 21437281
API_HASH = "6d8fd92d56b9b9db9377cc493fa641d0"
BOT_TOKEN = "8507472664:AAGQ_xlh-CLwCafVBGp5YPaBOmD_th4Oq88"

app = Client("yasser_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("🚀 **بوت ياسر اشتغل رسمياً!**\n\nالآن يمكنك استخدام الأوامر:\n🔹 `/price BTC` للسعر المباشر\n🔹 `/long` أو `/short` للصفقات")

@app.on_message(filters.command("price"))
async def get_price(client, message):
    try:
        symbol = message.command[1].upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        with urlopen(url) as response:
            data = json.loads(response.read())
            price = float(data['price'])
            await message.reply_text(f"💰 سعر **{symbol}** الآن: `${price:.4f}`")
    except:
        await message.reply_text("❌ اكتب العملة صح (مثال: `/price BTC`)")

# إضافة أوامر الصفقات (Long/Short) بنفس الطريقة السابقة هنا إذا أردت..

print("--- البوت والموقع انطلقا! ---")
app.run()
