# الوسيط الآمن

الوسيط الآمن بوابة محلية قبل أدوات الذكاء الاصطناعي: تعقم البريد، الجوال، المفاتيح، الأسرار، وتستدعي المناعة لمنع prompt injection قبل إرسال النص.

## أوامر

```powershell
python -m alwaseet_alamin.cli gate --text "hello user@example.com token='sk-12345678901234567890'"
python -m alwaseet_alamin.cli convert-neuralchemy
python -m alwaseet_alamin.cli batch --input data\benchmarks\alwaseet_neuralchemy_proxy.jsonl
```

الفرق عن المناعة: المناعة تحرس الوكلاء وأدواتهم، أما الوسيط يحرس البشر/الموظفين قبل خروج بياناتهم إلى AI.

## آخر نتائج

- الاختبارات الذاتية: 4/4 ناجحة.
- بيانات الإنترنت: Neuralchemy Prompt Injection بعدد 15,919 سجل، مع أسرار صناعية كل 23 سجل لاختبار DLP.
- Benchmark: 15,919 فحص، 0 أخطاء، 0 تسريب، F1=90.88%، Precision=97.43%، Recall=85.15%، Specificity=96.29%.
- Stress: 47,757 فحص، 0 أخطاء، 0 تسريب، p99=10.90ms، peak memory=14.38MB.

## تحسينات إنتاجية 2026-07-04

- لم تعد `findings` تحتفظ بالقيم الخام للأسرار؛ تحفظ نوع السر، الطول، وبصمة SHA-256 قصيرة فقط.
- أصبح اختبار التسريب في `batch/stress` يفحص كامل نتيجة الوسيط JSON، وليس `outbound` فقط.
- أضيف اختبار يثبت أن البريد ومفاتيح OpenAI لا تظهر في أي جزء من نتيجة `sanitize()`.

## التشغيل المؤسسي (Enterprise) — v1.0.0

- **بوابة DLP عبر HTTP**: `python -m alwaseet_alamin.cli serve` → `POST /api/gate {"text","user"}` يعيد `action/outbound/sanitization/immunity`.
- **ضمانة**: الأسرار لا تظهر خاماً في أي جزء من الرد (fingerprint فقط)، و`outbound` فارغ عند الحجب/الحجر.
- **نقاط فحص**: `/api/health` (مفتوح) · `/api/version` · `/api/metrics`.
- **تهيئة عبر البيئة**: متغيرات `ALWASEET_*` — انظر `docs/OPERATIONS.md`.
- **مصادقة**: `ALWASEET_API_KEY` → ترويسة `X-API-Key`. **سجلات JSON**: `logs\alwaseet-alamin.service.jsonl`.

## التشغيل المؤسسي (Enterprise) — v1.0.0

- **بوابة DLP عبر HTTP**: `python -m alwaseet_alamin.cli serve` → `POST /api/gate {"text","user"}` يعيد `action/outbound/sanitization/immunity`.
- **ضمانة**: الأسرار لا تظهر خاماً في أي جزء من الرد، و`outbound` فارغ عند الحجب/الحجر.
- **تغطية DLP موسعة (v1.0.0)**: مفاتيح دفع `sk_live_/pk_live_` (Stripe/Moyasar) + GitHub tokens + Slack tokens.
- **نقاط فحص**: `/api/health` (مفتوح) · `/api/version` · `/api/metrics`.
- **تهيئة عبر البيئة**: متغيرات `ALWASEET_*` — انظر `docs/OPERATIONS.md`.
- **مصادقة**: `ALWASEET_API_KEY` → ترويسة `X-API-Key`. **سجلات JSON**: `logs\alwaseet-alamin.service.jsonl`.
