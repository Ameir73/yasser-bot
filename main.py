import logging
import asyncio
import httpx
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# إعداد السجلات
logging.basicConfig(level=logging.INFO)

# --- [ البيانات الأساسية ] ---
API_TOKEN = '8507472664:AAEUQ5uZWTQtOXtbiBOdxnXLPKz4eFrOvXo'
ADMIN_ID = 7988144062

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

async def get_ai_description(word):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # طلب وصف ذكي جداً ومختصر
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user", 
                "content": f"أعطني وصفاً غامضاً وذكياً جداً لـ ({word}) دون ذكر اسمها أو أي حرف منها. اجعل الوصف يبدو كلغز شعري قصير جداً بالعربي."
            }
        ],
        "temperature": 0.5 # تقليل العشوائية ليكون الوصف دقيقاً
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            if response.status_code == 200:
                res = response.json()
                return res['choices'][0]['message']['content'].strip()
            return f"❌ خطأ API: {response.status_code}"
    except Exception as e:
        return f"🛠️ خطأ تقني: {str(e)}"

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    await m.answer("مرحباً بك في مختبر الذكاء. أرسل لي أي كلمة الآن وسأتحداك بوصفها!")

@dp.message_handler()
async def handle_testing(m: types.Message):
    # الاختبار لياسر فقط
    if m.from_user.id != ADMIN_ID:
        return

    word = m.text.strip()
    wait_msg = await m.answer(f"🔍 أحلل كلمة: <b>{word}</b>...")
    
    description = await get_ai_description(word)
    
    await wait_msg.edit_text(
        f"📦 **الكلمة:** {word}\n"
        f"📝 **الوصف الذكي:**\n\n{description}\n\n"
        f"---"
    )

if __name__ == '__main__':
    print("🚀 المختبر جاهز.. أرسل الكلمات في التليجرام يا ياسر")
    executor.start_polling(dp, skip_updates=True)
