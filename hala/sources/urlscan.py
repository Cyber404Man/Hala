"""مصدر urlscan.io — فحص URLs حقيقي

الوثائق: https://urlscan.io/docs/api/
مفتاح مجاني: https://urlscan.io/user/signup
"""
import httpx

BASE = "https://urlscan.io/api/v1"


class UrlscanError(Exception):
    """خطأ في urlscan"""
    pass


async def search_domain(domain: str, api_key: str) -> list[dict]:
    """
    يبحث عن scans سابقة لنطاق في urlscan.

    Returns:
        قائمة نتائج. فاضية إذا ما في scans.
    """
    if not api_key:
        return []

    url = f"{BASE}/search/?q=domain:{domain}"
    headers = {"api-key": api_key}

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(url, headers=headers)
        except httpx.RequestError as e:
            raise UrlscanError(f"فشل الاتصال: {e}") from e

        if r.status_code == 401:
            raise UrlscanError("مفتاح urlscan غير صالح")

        if r.status_code == 429:
            raise UrlscanError("تجاوزت الحد — انتظر شوي")

        if r.status_code != 200:
            return []

        data = r.json()

    results = data.get("results", [])

    return [
        {
            "source": "urlscan",
            "url": item.get("page", {}).get("url"),
            "domain": item.get("page", {}).get("domain"),
            "ip": item.get("page", {}).get("ip"),
            "country": item.get("page", {}).get("country"),
            "server": item.get("page", {}).get("server"),
            "scan_date": item.get("task", {}).get("time"),
            "verdicts": item.get("verdicts", {}),
            "screenshot": item.get("screenshot"),
        }
        for item in results[:10]
    ]


async def check_if_live(domain: str, api_key: str) -> dict | None:
    """
    يتحقق إذا النطاق مسجّل وله scan في urlscan.

    Returns:
        dict فيه معلومات الscan، أو None إذا ما في.
    """
    results = await search_domain(domain, api_key)
    return results[0] if results else None