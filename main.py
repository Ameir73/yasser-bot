from pyrogram import Client, filters
import requests

# بياناتك المحفوظة
api_id = 21437281
api_hash = "6d8fd92d56b9b9db9377cc493fa641d0"
bot_token = "8507472664:AAGQ_xlh-CLwCafVBGp5YPaBOmD_th4Oq88"

app = Client("yasser_pro_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# 1. أمر البداية والمعلومات
@app.on_message(filters.command("start"))
async def start(client, message):
    info_text = (
        "👋 **أهلاً بك في بوت التداول الاحترافي!**\n\n"
        "👤 **المطور:** ياسر\n"
        "🛡️ **الاستراتيجية:** انفجار السيولة وقنص الارتدادات\n\n"
        "🚀 **الأوامر المتاحة:**\n"
        "🔹 `/price [العملة]` - لسعر العملة المباشر\n"
        "🔹 `/long [العملة] [السعر]` - توصية شراء\n"
        "🔹 `/short [العملة] [السعر]` - توصية بيع"
    )
    await message.reply_text(info_text, disable_web_page_preview=True)

# 2. أمر جلب السعر المباشر
@app.on_message(filters.command("price"))
async def get_price(client, message):
    try:
        coin = message.command[1].upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT"
        data = requests.get(url).json()
        price = data['price']
        await message.reply_text(f"💰 سعر عملة **{coin}** الآن هو: `${float(price):.4f}`")
    except:
        await message.reply_text("❌ تأكد من كتابة اسم العملة بشكل صحيح (مثال: `/price BTC`)")

# 3. أمر صفقات الشراء (Long)
@app.on_message(filters.command("long"))
async def long_trade(client, message):
    try:
        coin = message.command[1].upper()
        entry = float(message.command[2])
        msg = (
            f"🔥 فرصة انفجار سعري: #{coin}USDT 🚀\n\n"
            f"🎯 منطقة الدخول: {entry:.4f}\n"
            f"💰 الأهداف: {entry*1.02:.4f} | {entry*1.05:.4f} | {entry*1.08:.4f}\n"
            f"🚫 وقف الخسارة: {entry*0.95:.4f}\n\n"
            f"القرار: دخول قوي (Long) 📈"
        )
        await message.reply_text(msg)
    except:
        await message.reply_text("مثال: `/long FET 0.2855`")

# 4. أمر صفقات البيع (Short)
@app.on_message(filters.command("short"))
async def short_trade(client, message):
    try:
        coin = message.command[1].upper()
        entry = float(message.command[2])
        msg = (
            f"📉 فرصة هبوط (Short): #{coin}USDT\n\n"
            f"🎯 منطقة الدخول: {entry:.4f}\n"
            f"💰 الأهداف: {entry*0.98:.4f} | {entry*0.95:.4f} | {entry*0.92:.4f}\n"
            f"🚫 وقف الخسارة: {entry*1.05:.4f}\n\n"
            f"القرار: بيع (Short) 📉"
        )
        await message.reply_text(msg)
    except:
        await message.reply_text("مثال: `/short BTC 50000`")

print("البوت الخارق يعمل...")
app.run()
        
