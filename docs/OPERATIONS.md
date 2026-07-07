# دليل تشغيل alwaseet_alamin (Operations Runbook)

## 1) التهيئة عبر متغيرات البيئة

| المتغير | الافتراضي | الوظيفة |
|---|---|---|
| `ALWASEET_HOME` | جذر المشروع | مجلد الحالة (logs) |
| `ALWASEET_API_KEY` | (فارغ = بلا مصادقة) | إن ضُبط: كل `/api/*` عدا health يتطلب `X-API-Key` |
| `ALWASEET_HOST` / `ALWASEET_PORT` | `127.0.0.1` / `8795` | عنوان الخدمة |
| `ALWASEET_MAX_BODY_BYTES` | `1048576` | حد حجم الطلب (413 عند التجاوز) |
| `ALWASEET_LOG_DIR` / `ALWASEET_LOG_LEVEL` | `<home>\logs` / `INFO` | سجلات JSON منظمة |

## 2) تشغيل الخدمة

```powershell
$env:ALWASEET_API_KEY = "مفتاح-قوي"
python -m alwaseet_alamin.cli serve
```

## 3) نقاط الفحص المشتركة

- `GET /api/health` — مفتوح دائماً (للـ probes): `{ok, service, version, uptime_s, auth_required}`.
- `GET /api/version` — إصدار الخدمة.
- `GET /api/metrics` — عدادات + p50/p95/p99 زمن المعالجة.

نقاط النطاق موثقة في `README.md`.

## 4) السجلات

`logs\alwaseet-alamin.service.jsonl` — JSON سطري لكل طلب `{path, status, ms}` بتدوير تلقائي 5MB × 3 نسخ.

## 5) الحوادث الشائعة

| العرض | السبب المرجح | العلاج |
|---|---|---|
| `401` لكل الطلبات | مفتاح API غير مطابق | طابق `X-API-Key` مع `ALWASEET_API_KEY` |
| `413` | حمولة أكبر من الحد | ارفع `ALWASEET_MAX_BODY_BYTES` أو قسّم الطلب |
| بطء p99 | حمولات ضخمة أو موارد مشغولة | راقب `/api/metrics` وقلل حجم الدفعات |

## 6) الترقية

1. أوقف الخدمة → حدّث الكود.
2. `python -m unittest discover -s tests -v` (يجب أن تنجح كلها).
3. أعد التشغيل وتحقق من `/api/health`.
