import os
import asyncio
from aiohttp import web
from pyrogram import Client, filters
import requests

# بياناتك
API_ID = 21437281
API_HASH = "6d8fd92d56b9b9db9377cc493fa641d0"
BOT_TOKEN = "8507472664:AAGQ_xlh-CLwCafVBGp5YPaBOmD_th4Oq88"

# 1. خادم ويب صغير جداً لإرضاء Render
async def handle(request):
    return web.Response(text="Bot is Live!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# 2. تشغيل البوت
app = Client("yasser_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("🚀 أهلاً ياسر! البوت شغال 100% الآن.\nجرب `/price BTC` فوراً!")

@app.on_message(filters.command("price"))
async def get_price(client, message):
    try:
        symbol = message.command[1].upper()
        res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT").json()
        price = float(res['price'])
        await message.reply_text(f"💰 سعر **{symbol}** الآن: `${price:.2f}`")
    except:
        await message.reply_text("❌ اكتب العملة صح")

async def main():
    await start_web_server()
    await app.start()
    print("--- البوت انطلق بنجاح ---")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
    
