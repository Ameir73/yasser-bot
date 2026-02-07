from pyrogram import Client, filters

# بياناتك الأساسية
api_id = 21437281
api_hash = "6d8fd92d56b9b9db9377cc493fa641d0"
bot_token = "8507472664:AAGQ_xlh-CLwCafVBGp5YPaBOmD_th4Oq88"

app = Client("yasser_session", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# رسالة الترحيب عند البداية
@app.on_message(filters.command("start"))
async def start(client, message):
    welcome_text = (
        "أهلاً بك يا ياسر في بوت التداول الخاص بك! 🚀\n\n"
        "أنا جاهز لنشر الصفقات الآن. استخدم الأوامر التالية:\n"
        "🟢 /long [العملة] [السعر] - لنشر صفقة شراء\n"
        "🔴 /short [العملة] [السعر] - لنشر صفقة بيع"
    )
    await message.reply_text(welcome_text)

# أمر نشر صفقة شراء (Long)
@app.on_message(filters.command("long"))
async def long_trade(client, message):
    try:
        args = message.command
        coin = args[1].upper()
        price = args[2]
        template = (
            f"📊 تحليل تقني: #{coin}USDT ⚡\n\n"
            f"**الاتجاه الحالي:** صعودي (Bullish) 🟢\n\n"
            f"**📐 مستويات التداول:**\n"
            f"* **نقطة الدخول:** {price}\n"
            f"* **القرار الفني:** شراء (Long) بناءً على استراتيجية انفجار السيولة. 📈\n\n"
            f"#BinanceHODLerBREV #ETHWhaleWatch #BTCVSGOLD"
        )
        await message.reply_text(template)
    except:
        await message.reply_text("يا ياسر، اكتب الأمر هكذا: /long BTC 50000")

# أمر نشر صفقة بيع (Short)
@app.on_message(filters.command("short"))
async def short_trade(client, message):
    try:
        args = message.command
        coin = args[1].upper()
        price = args[2]
        template = (
            f"منشور صفقة {coin}USDT (جاهز للنسخ - بيع Short) 📉\n"
            f"بيع (SHORT): #{coin}USDT\n"
            f"نطاق الدخول: {price}\n"
            f"اضغط أدناه وافتح صفقة بيع (Short) 📉"
        )
        await message.reply_text(template)
    except:
        await message.reply_text("يا ياسر، اكتب الأمر هكذا: /short BTC 50000")

print("بوت الصفقات يعمل بنجاح...")
app.run()
