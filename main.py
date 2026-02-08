# --- الرابط المحدث لحل مشكلة الـ DNS ---
MONGO_URI = "mongodb+srv://yasser_user:YasserPass2026@cluster0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    # إضافة tlsAllowInvalidCertificates لضمان تخطي مشاكل الاتصال في Render
    client = pymongo.MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
    db = client['YasserQuiz']
    q_collection = db['questions']
    print("✅ تم حل مشكلة الاتصال بنجاح!")
except Exception as e:
    print(f"❌ لا زال هناك خطأ: {e}")
    
