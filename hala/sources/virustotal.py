"""مصدر VirusTotal — كشف malware/phishing

الوثائق: https://developers.virustotal.com/reference
مفتاح مجاني: https://www.virustotal.com/gui/join-us
500 req/day
"""
import httpx

BASE = "https://www.virustotal.com/api/v3"


class VirusTotalError(Exception):
    pass


async def check_domain(domain: str, api_key: str) -> dict | None:
    """
    يفحص نطاق في VirusTotal.
    """
    if not api_key:
        return None

    url = f"{BASE}/domains/{domain}"
    headers = {"x-apikey": api_key}

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(url, headers=headers)
        except httpx.RequestError as e:
            raise VirusTotalError(f"فشل الاتصال: {e}") from e

        if r.status_code == 404:
            return None
        if r.status_code == 401:
            raise VirusTotalError("مفتاح VirusTotal غير صالح")
        if r.status_code == 429:
            raise VirusTotalError("تجاوزت الحد — انتظر شوي")
        if r.status_code != 200:
            return None

        data = r.json()

    attrs = data.get("data", {}).get("attributes", {})
    stats = attrs.get("last_analysis_stats", {})

    return {
        "source": "virustotal",
        "domain": domain,
        "reputation": attrs.get("reputation", 0),
        "malicious": stats.get("malicious", 0),
        "suspicious": stats.get("suspicious", 0),
        "harmless": stats.get("harmless", 0),
        "undetected": stats.get("undetected", 0),
        "categories": attrs.get("categories", {}),
        "registrar": attrs.get("registrar"),
        "creation_date": attrs.get("creation_date"),
    }
