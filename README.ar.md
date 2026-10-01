# HALA 

> **Hunting Arab Leaks & Assets**
> أول أداة مفتوحة المصدر لاستخبارات التهديدات بالعربية.

[![CI](https://github.com/Cyber404Man/Hala/actions/workflows/ci.yml/badge.svg)](https://github.com/Cyber404Man/Hala/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

🇬🇧 [Read in English](README.md)

---

## ليش HALA؟

كل أدوات استخبارات التهديدات العالمية مبنية للغرب. بتفهم إنجليزي، بتراقب Twitter وReddit، وبتتجاهل المنصات اللي بيستخدمها العرب فعلاً.

وبنفس الوقت، **400+ مليون ناطق بالعربي** بيواجهوا:
- تصيّد باللهجات العربية المحلية
- تسريب أرقام من شركات اتصال إقليمية
- صفحات OTP مزيفة تستهدف بنوك عربية
- رسائل احتيال على تليجرام وواتساب وفيسبوك

**HALA مبنية لأجلهم.**

---

## الأوامر

| الأمر | الوظيفة |
|-------|---------|
| `hala kashif <phone>` | فحص رقم هاتف عربي في تسريبات معروفة |
| `hala sitr` | روابط رسمية لحذف بياناتك من مواقع عربية وعالمية |
| `hala athar @username` | OSINT على 16 منصة عربية وعالمية |
| `hala sayyad --brand "jawwal"` | توليد نطاقات تصيّد محتملة على براند عربي |
| `hala nlp --text "..."` | كشف مؤشرات الاحتيال في رسالة عربية |

---

## التثبيت

```bash
pip install hala-arab
أو من المصدر:

bash
git clone https://github.com/Cyber404Man/Hala.git
cd Hala
pip install -e ".[dev]"
أمثلة سريعة
فحص رقم هاتف
bash
hala kashif 0599123456 --region PS
hala kashif +967712345678
hala kashif 0501234567 --region SA --json-out
نظّف بصمتك الرقمية
bash
hala sitr
hala sitr --country PS
hala sitr --open
OSINT على username
bash
hala athar @torvalds
hala athar @username --only-found
صيد نطاقات تصيّد
bash
hala sayyad --brand jawwal --dialect ps
hala sayyad --brand "زين" --suspicious-only
كشف رسالة احتيال
bash
hala nlp --text "مبروك! فزت بجائزة 5000 شيكل، اضغط الرابط"
# → احتيال مؤكد (85/100)
الأخلاقيات والقانون
HALA أداة دفاعية فقط.

✅ نستخدم metadata من إفصاحات التسريبات العامة

✅ نستعلم APIs رسمية (HaveIBeenPwned) عند توفر المفتاح

✅ نولّد روابط حذف رسمية من مواقع تجميع البيانات

❌ لا نحمّل ملفات تسريبات

❌ لا نسحب بيانات من بوتات تليجرام أو جروبات فيسبوك غير قانونية

❌ لا نخزّن بيانات شخصية لأي فرد

كل ميزة تمر من فلتر: "هل هذا يحمي الناطقين بالعربية، أم يضر أحد؟"

خارطة الطريق
☑ hala kashif — فحص تسريبات الأرقام
☑ hala sitr — روابط حذف البيانات
☑ hala athar — OSINT عربي
☑ hala sayyad — توليد نطاقات تصيّد
☑ hala nlp — كشف الاحتيال (rule-based)
□ HALA-NLP — LLM عربي متخصص بالأمن
□ HALA-API — REST API للبنوك والاتصالات
□ HALA-Graph — graph لربط شبكات المحتالين
□ HALA-Honeypot — اصطياد المحتالين
□ HALA-Vision — كشف التصيّد بالصور
المساهمة
نرحّب بمساهمات الباحثين والمطورين العرب في الأمن السيبراني.

طرق المساهمة:

أضف metadata لتسريبات عربية جديدة (بدون بيانات شخصية!)

حسّن أنماط الاحتيال في scam_patterns.json

أضف روابط حذف من بلدك

ترجم الـREADME للهجات عربية أخرى

بلّغ عن false positives / negatives

الترخيص
MIT © HALA Community

بُني في غزة. لأجل 400+ مليون ناطق بالعربية. 🇵🇸
