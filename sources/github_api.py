"""GitHub API — معلومات حقيقية عن المستخدمين

الوثائق: https://docs.github.com/en/rest
بدون مفتاح: 60 req/hour
مع مفتاح: 5000 req/hour
"""
import httpx

BASE = "https://api.github.com"


class GitHubError(Exception):
    pass


async def get_user(username: str, token: str | None = None) -> dict | None:
    """يجيب معلومات مستخدم GitHub."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(f"{BASE}/users/{username}", headers=headers)
        except httpx.RequestError as e:
            raise GitHubError(f"فشل الاتصال: {e}") from e

        if r.status_code == 404:
            return None
        if r.status_code == 403:
            raise GitHubError("تجاوزت الحد — جرّب بعد ساعة أو أضف token")
        if r.status_code != 200:
            return None

        data = r.json()

    return {
        "source": "github",
        "username": data.get("login"),
        "name": data.get("name"),
        "bio": data.get("bio"),
        "location": data.get("location"),
        "company": data.get("company"),
        "blog": data.get("blog"),
        "public_repos": data.get("public_repos"),
        "followers": data.get("followers"),
        "following": data.get("following"),
        "created_at": data.get("created_at"),
        "avatar_url": data.get("avatar_url"),
        "profile_url": data.get("html_url"),
    }
