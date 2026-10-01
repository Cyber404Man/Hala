"""مصدر XposedOrNot — فحص إيميلات مجاني 100%

الوثائق: https://xposedornot.com/api_doc
بدون مفتاح. بدون تسجيل.
"""
import httpx

BASE = "https://api.xposedornot.com/v1"


class XposedError(Exception):
    """خطأ في XposedOrNot"""
    pass


async def check_email(email: str) -> list[dict]:
    """
    يفحص إيميل في XposedOrNot.

    Returns:
        قائمة تسريبات. فاضية إذا نظيف.
    """
    url = f"{BASE}/check-email/{email}"

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(url)
        except httpx.RequestError as e:
            raise XposedError(f"فشل الاتصال: {e}") from e

        if r.status_code == 404:
            return []  # ما لقينا

        if r.status_code == 429:
            raise XposedError("تجاوزت الحد — انتظر شوي")

        if r.status_code != 200:
            raise XposedError(f"خطأ {r.status_code}")

        try:
            data = r.json()
        except Exception:
            return []

    # XposedOrNot بيرجع أشكال مختلفة حسب النتيجة
    breaches = []

    # لو رجع { "breaches": ["Adobe", "LinkedIn", ...] }
    if isinstance(data, dict):
        raw = data.get("breaches") or data.get("breach") or []
        if isinstance(raw, list) and raw and isinstance(raw[0], list):
            # أحيانًا nested: [["Adobe", "LinkedIn"]]
            raw = raw[0]
        for name in raw:
            breaches.append({
                "source": "xposedornot",
                "name": name if isinstance(name, str) else str(name),
                "title": name if isinstance(name, str) else str(name),
                "date": None,
                "records": None,
                "data_classes": [],
            })

    return breaches
