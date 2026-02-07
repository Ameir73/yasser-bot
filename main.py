from pyrogram import Client, filters

# بياناتك الصحيحة (تأكد من عدم وجود مسافات)
api_id = 21437281
api_hash = "6d8fd92d56b9b9db9377cc493fa641d0"
bot_token = "7820755909:AAH6KNo2o9u_FpE6p3_Y8P3O9v87K-X4E_w"

app = Client("yasser_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("أهلاً بك يا ياسر! البوت الخاص بك يعمل الآن بنجاح على سيرفر Render. 🚀")

print("البوت بدأ العمل...")
app.run()
