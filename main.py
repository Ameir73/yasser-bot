from pyrogram import Client, filters

# بياناتك المحفوظة
api_id = 21437281
api_hash = "6d8fd92d56b9b9db9377cc493fa641d0"
bot_token = "8507472664:AAGQ_xlh-CLwCafVBGp5YPaBOmD_th4Oq88"

app = Client("yasser_pro_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def start(client, message):
    # لستة معلومات جميلة عن صاحب البوت
    info_text = (
        "👋 **أهلاً بك في بوت الصفقات الذكي!**\n\n"
        "✨ **معلومات حول المطور:**\n"
        "👤 **الاسم:** ياسر\n"
        "🎯 **الهدف:** تحقيق الأهداف المالية خلال عام\n"
        "🛡️ **الاستراتيجية:** قنص الارتدادات وانفجار السيولة\n"
        "💻 **المطور على GitHub:** [Ameir73](https://github.com/Ameir73)\n\n"
        "🚀 **كيفية الاستخدام:**\n"
        "لتحليل صفقة ونشرها، أرسل الأمر التالي:\n"
        "`/trade [العملة] [السعر]`\n\n"
        "مثال: `/trade FET 0.2855`"
    )
    await message.reply_text(info_text, disable_web_page_preview=True)

@app.on_message(filters.command("trade"))
async def trade_logic(client, message):
    try:
        args = message.command
        coin = args[1].upper()
        entry_price = float(args[2])
        
        # حساب الأهداف تلقائياً
        tp1 = entry_price * 1.02
        tp2 = entry_price * 1.05
        tp3 = entry_price * 1.08
        sl = entry_price * 0.95 
        
        template = (
            f"🔥 فرصة انفجار سعري: #{coin}USDT 🚀\n\n"
            f"انطلاقة جديدة لعملة {coin} الآن! 💪\n\n"
            f"📐 خطة الهجوم:\n"
            f"🎯 منطقة الدخول: {entry_price:.4f}\n"
            f"🛡️ تأمين الصفقة (DCA): {entry_price * 0.97:.4f}\n"
            f"🚫 وقف الخسارة (SL): {sl:.4f}\n\n"
            f"💰 محطات جني الأرباح:\n"
            f"1️⃣ الهدف الأول: {tp1:.4f} ⚡\n"
            f"2️⃣ الهدف الثاني: {tp2:.4f} 🚀\n"
            f"3️⃣ الهدف الثالث: {tp3:.4f} 🚀🚀\n\n"
            f"القرار: دخول قوي (Long) بناءً على استراتيجية 'انفجار السيولة'."
        )
        await message.reply_text(template)
    except Exception as e:
        await message.reply_text("يرجى كتابة الأمر بشكل صحيح، مثال:\n/trade FET 0.2855")

print("البوت يعمل مع لستة المعلومات...")
app.run()
