📱 Android AI Agent - Gemini Vision Assistant

""Python" (https://img.shields.io/badge/Python-3.8%2B-blue.svg)" (https://www.python.org/)
""Flask" (https://img.shields.io/badge/Flask-2.0%2B-green.svg)" (https://flask.palletsprojects.com/)
""Gemini" (https://img.shields.io/badge/Gemini-Vision-orange.svg)" (https://ai.google.dev/)

««وكيل ذكي للتحكم بهاتف Android باستخدام Gemini Vision AI - يرى الشاشة، يحللها، وينفذ المهام تلقائياً»»

---

✨ المميزات

- 🧠 ذكاء اصطناعي متطور - يستخدم Gemini Vision لتحليل الشاشة وفهم المحتوى.
- 👁️ رؤية الشاشة - يلتقط لقطات شاشة ويحللها بدقة عالية.
- 🎯 تحديد إحداثيات دقيق - يحدد مواقع العناصر على الشاشة.
- 🤖 تنفيذ المهام - نقر، سحب، كتابة، فتح تطبيقات، والتحكم الكامل.
- 💬 واجهة دردشة - تحدث مع الوكيل بلغتك الطبيعية.
- 📱 دعم Shizuku - تحكم متقدم بدون صلاحيات Root.
- 🗄️ ذاكرة مدمجة - يتعلم من التفاعلات السابقة ويتذكر التطبيقات.

---

🚀 متطلبات التشغيل

📱 على الهاتف

- Android 8.0+
- Shizuku مثبت ومشغل ("تحميل Shizuku" (https://shizuku.rikka.app/))
- ADB أو Termux مع Rish

💻 على الكمبيوتر

- Python 3.8+
- ADB (Android Debug Bridge)

---

📦 التثبيت

1. استنساخ المشروع

git clone https://github.com/drox/android-ai-agent.git
cd android-ai-agent

2. تثبيت المتطلبات

pip install -r requirements.txt

3. إعداد Gemini API Key

احصل على مفتاح API من "Google AI Studio" (https://aistudio.google.com/).

ثم قم بتعيينه كمتغير بيئي:

export GEMINI_API_KEY="your_api_key_here"

أو ضعه مباشرة في "agent.py":

GEMINI_API_KEY = "your_api_key_here"

«⚠️ لا تشارك مفتاح API الخاص بك أو ترفعه إلى GitHub.»

---

🔧 الإعدادات المسبقة

تشغيل Shizuku على الهاتف

1. قم بتثبيت تطبيق Shizuku.
2. فعّل Shizuku عبر ADB أو Root.
3. امنح Shizuku صلاحيات Termux إذا كنت تستخدم Termux.

تشغيل ADB

adb devices
adb shell

---

▶️ التشغيل

تشغيل الخادم

python agent.py

فتح الواجهة

افتح المتصفح على:

http://localhost:5000

---

🧠 كيفية العمل

1. التقاط الشاشة ← يلتقط لقطة للشاشة الحالية.
2. تحليل Gemini Vision ← يرسل الصورة مع المطلوب إلى Gemini.
3. تحديد الإجراء ← يستنتج الإجراء المناسب والإحداثيات.
4. التنفيذ ← ينفذ الأمر عبر Shizuku/ADB.
5. التعلم ← يحفظ المعلومات في قاعدة البيانات.

---

🛠️ الأوامر المدعومة

الأمر| الوصف
"افتح واتساب"| فتح تطبيق WhatsApp
"اضغط على زر X"| النقر على عنصر معين
"اكتب رسالة"| كتابة نص في الحقل المحدد
"اسحب للأعلى"| تمرير الشاشة
"رجوع"| الضغط على زر الرجوع
"الرئيسية"| العودة للشاشة الرئيسية
"ساعدني"| شرح ما يمكن للوكيل فعله

---

📂 هيكل المشروع

android-ai-agent/
├── agent.py                    # الوكيل الرئيسي + API
├── requirements.txt            # المتطلبات
├── templates/
│   └── index.html              # واجهة المستخدم
├── memory.db                   # قاعدة البيانات (تُنشأ تلقائياً)
└── README.md

---

📊 قاعدة البيانات

يستخدم SQLite لتخزين:

- 💬 المحادثات - سجل التفاعلات.
- 📱 التطبيقات المكتشفة - التطبيقات المثبتة واستخداماتها.
- 🧠 تحليلات الشاشة - تحليلات سابقة.

---

🔌 API Endpoints

المسار| الطريقة| الوصف
"/"| "GET"| واجهة المستخدم
"/api/chat"| "POST"| إرسال رسالة وتنفيذ مهمة
"/api/status"| "GET"| حالة الاتصال والمعلومات
"/api/screenshot"| "GET"| الحصول على لقطة شاشة
"/api/apps"| "GET"| قائمة التطبيقات المثبتة
"/api/analyze"| "POST"| تحليل الشاشة فقط
"/api/tap"| "POST"| النقر على إحداثيات محددة
"/api/history"| "GET"| تاريخ المحادثة

---

🎨 واجهة المستخدم

- 🌑 تصميم عصري - تصميم داكن وجذاب.
- 📱 شاشة مصغرة - عرض مباشر للشاشة.
- ⚡ أزرار سريعة - وصول سريع للتطبيقات الشائعة.
- ⌨️ مؤشر الكتابة - يعرفك أن الوكيل يعمل.
- 🟢 حالة الاتصال - يعرض حالة Shizuku.

---

⚠️ ملاحظات هامة

1. صلاحيات Shizuku - تأكد من تشغيل Shizuku قبل الاستخدام.
2. مفتاح Gemini API - مطلوب للتحليل البصري.
3. اتصال ADB - يجب أن يكون الهاتف متصلاً بالكمبيوتر عند استخدام ADB.
4. بعض التطبيقات - قد لا تعمل إذا كانت محمية أو مخفية.

---

🐛 استكشاف الأخطاء

المشكلة| الحل
Shizuku غير متصل| أعد تشغيل Shizuku وتأكد من تفعيله
لا تظهر الشاشة| تحقق من اتصال ADB باستخدام "adb devices"
خطأ في Gemini| تحقق من صحة مفتاح API
لا يستجيب الوكيل| تأكد من تشغيل الخادم وفحص المنفذ

---

📝 التطوير المستقبلي

- [ ] دعم المزيد من نماذج الذكاء الاصطناعي
- [ ] واجهة مستخدم محسّنة للجوال
- [ ] تنفيذ مهام متعددة الخطوات
- [ ] تعلم تلقائي من التفاعلات
- [ ] دعم التحكم الصوتي

---

🙏 الشكر والتقدير

- Google Gemini Vision API - للتحليل البصري والذكاء الاصطناعي.
- Shizuku - للتحكم المتقدم في Android.
- Flask - خادم ويب خفيف وسريع.

---

📞 التواصل

📸 Instagram

""Instagram" (https://img.shields.io/badge/Instagram-rayan__71x-E4405F?logo=instagram&logoColor=white)" (https://instagram.com/rayan_71x)

✈️ Telegram

""Telegram" (https://img.shields.io/badge/Telegram-drox71-26A5E4?logo=telegram&logoColor=white)" (https://t.me/drox71)

---

📜 الترخيص

هذا المشروع مرخص تحت MIT License - يمكنك استخدامه وتعديله بحرية وفق شروط الترخيص.

---

⭐ دعم المشروع

إذا أعجبك المشروع، لا تنسَ منحه ⭐ على GitHub!