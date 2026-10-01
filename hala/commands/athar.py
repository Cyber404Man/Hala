"""hala athar - أثر: OSINT عربي على username"""
import asyncio
import json
import click
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# منصات عربية + عالمية مهمة للمستخدم العربي
PLATFORMS = [
    {"name": "GitHub",     "url": "https://github.com/{u}",          "check": "status"},
    {"name": "TikTok",     "url": "https://www.tiktok.com/@{u}",     "check": "status"},
    {"name": "Facebook",   "url": "https://www.facebook.com/{u}",    "check": "status"},
    {"name": "Instagram",  "url": "https://www.instagram.com/{u}/",  "check": "status"},
    {"name": "Telegram",   "url": "https://t.me/{u}",                "check": "telegram"},
    {"name": "Ask.fm",     "url": "https://ask.fm/{u}",              "check": "status"},
    {"name": "Pinterest",  "url": "https://www.pinterest.com/{u}/",  "check": "status"},
    {"name": "Reddit",     "url": "https://www.reddit.com/user/{u}","check": "status"},
    {"name": "YouTube",    "url": "https://www.youtube.com/@{u}",    "check": "status"},
    {"name": "Snapchat",   "url": "https://www.snapchat.com/add/{u}","check": "status"},
    {"name": "Behance",    "url": "https://www.behance.net/{u}",     "check": "status"},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{u}",      "check": "status"},
    {"name": "Medium",     "url": "https://medium.com/@{u}",         "check": "status"},
    {"name": "Twitch",     "url": "https://www.twitch.tv/{u}",       "check": "status"},
    {"name": "VK",         "url": "https://vk.com/{u}",              "check": "status"},
    {"name": "Mastodon",   "url": "https://mastodon.social/@{u}",    "check": "status"},
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


async def check_platform(client: httpx.AsyncClient, platform: dict, username: str) -> dict:
    """يفحص منصة وحدة."""
    url = platform["url"].format(u=username)
    result = {
        "name": platform["name"],
        "url": url,
        "found": False,
        "status": "-",
    }
    try:
        r = await client.get(url, follow_redirects=True, timeout=10)
        result["status"] = r.status_code

        if platform["check"] == "status":
            result["found"] = r.status_code == 200
        elif platform["check"] == "telegram":
            # تليجرام بيرجع 200 حتى للحسابات الوهمية — نتحقق من العنوان
            result["found"] = (
                r.status_code == 200 and "tgme_page_title" in r.text
            )
    except Exception as e:
        result["status"] = f"ERR: {type(e).__name__}"
    return result


async def scan_all(username: str) -> list[dict]:
    """يفحص كل المنصات بالتوازي."""
    async with httpx.AsyncClient(headers=HEADERS) as client:
        tasks = [check_platform(client, p, username) for p in PLATFORMS]
        return await asyncio.gather(*tasks)


@click.command()
@click.argument("username")
@click.option("--json-out", is_flag=True, help="إخراج JSON")
@click.option("--only-found", is_flag=True, help="اعرض النتائج الموجودة فقط")
def athar(username: str, json_out: bool, only_found: bool):
    """أثر - ابحث عن username على المنصات العربية والعالمية."""
    u = username.lstrip("@")

    if not u:
        console.print("[red]✗ لازم تكتب username.[/red]")
        raise SystemExit(2)

    if not json_out:
        console.print(Panel.fit(
            f"[bold]🔍 نبحث عن:[/bold] @{u}\n"
            f"[dim]عبر {len(PLATFORMS)} منصة[/dim]",
            title="[red]HALA · أثر[/red]",
            border_style="red",
        ))

    results = asyncio.run(scan_all(u))
    found = [r for r in results if r["found"]]

    if json_out:
        click.echo(json.dumps(found, ensure_ascii=False, indent=2))
        return

    # الجدول
    table = Table(title="نتائج البحث", show_lines=True)
    table.add_column("المنصة", style="cyan", no_wrap=True)
    table.add_column("الحالة", no_wrap=True)
    table.add_column("الرابط", style="blue", overflow="fold")

    rows = found if only_found else results
    for r in rows:
        if r["found"]:
            status = "[green]✓ موجود[/green]"
        else:
            status = "[dim]✗ غير موجود[/dim]"
        table.add_row(r["name"], status, r["url"])

    console.print(table)

    if found:
        console.print(f"\n[bold green]✓ لقينا {len(found)} من {len(results)} منصة.[/bold green]")
    else:
        console.print(f"\n[yellow]ما لقينا @{u} في أي منصة.[/yellow]")
        console.print("[dim]جرّب صيغ مختلفة (_, ., -) أو أرقام.[/dim]")
