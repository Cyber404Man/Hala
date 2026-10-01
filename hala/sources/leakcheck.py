"""مصدر LeakCheck.io — فحص إيميل + رقم

الوثائق: https://leakcheck.io/api
100 نتيجة/شهر مجانًا (بدون مفتاح)
"""
import httpx

BASE = "https://leakcheck.io/api/public"


class LeakCheckError(Exception):
    """خطأ في LeakCheck"""
    pass


async def check(target: str) -> list[dict]:
    """
    يفحص إيميل أو رقم في LeakCheck.

    Returns:
        قائمة مصادر التسريب. فاضية إذا نظيف.
    """
    url = f"{BASE}?check={target}"

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(
                url,
                headers={"User-Agent": "HALA-CLI"},
            )
        except httpx.RequestError as e:
            raise LeakCheckError(f"فشل الاتصال: {e}") from e

        if r.status_code == 429:
            raise LeakCheckError("تجاوزت الحد الشهري المجاني")

        if r.status_code != 200:
            raise LeakCheckError(f"خطأ {r.status_code}")

        data = r.json()

    if not data.get("found"):
        return []

    sources = data.get("sources") or []
    return [
        {
            "source": "leakcheck",
            "name": s.get("name", "unknown"),
            "title": s.get("name", "unknown"),
            "date": s.get("date"),
            "records": s.get("records"),
            "data_classes": s.get("fields", []),
        }
        for s in sources
    ]