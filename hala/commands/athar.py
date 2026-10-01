"""hala athar — أثر: OSINT عربي على username"""
import asyncio
import json
import click
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hala.sources import github_api

console = Console()

# تصنيف المنصات
PLATFORMS = [
    # عربية
    {"name": "Telegram", "url": "https://t.me/{u}", "check": "telegram", "region": "arab"},
    {"name": "Ask.fm", "url": "https://ask.fm/{u}", "check": "status", "region": "arab"},
    {"name": "Snapchat", "url": "https://www.snapchat.com/add/{u}", "check": "status", "region": "arab"},
    # عالمية
    {"name": "Instagram", "url": "https://www.instagram.com/{u}/", "check": "status", "region": "global"},
    {"name": "Facebook", "url": "https://www.facebook.com/{u}", "check": "status", "region": "global"},
    {"name": "Twitter/X", "url": "https://nitter.net/{u}", "check": "status", "region": "global"},
    {"name": "TikTok", "url": "https://www.tiktok.com/@{u}", "check": "status", "region": "global"},
    {"name": "YouTube", "url": "https://www.youtube.com/@{u}", "check": "status", "region": "global"},
    {"name": "Pinterest", "url": "https://www.pinterest.com/{u}/", "check": "status", "region": "global"},
    {"name": "Reddit", "url": "https://www.reddit.com/user/{u}", "check": "status", "region": "global"},
    {"name": "Twitch", "url": "https://www.twitch.tv/{u}", "check": "status", "region": "global"},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{u}", "check": "status", "region": "global"},
    # تقنية
    {"name": "GitHub", "url": "https://github.com/{u}", "check": "github", "region": "tech"},
    {"name": "GitLab", "url": "https://gitlab.com/{u}", "check": "status", "region": "tech"},
    {"name": "Medium", "url": "https://medium.com/@{u}", "check": "status", "region": "tech"},
    {"name": "Dev.to", "url": "https://dev.to/{u}", "check": "status", "region": "tech"},
    {"name": "Behance", "url": "https://www.behance.net/{u}", "check": "status", "region": "tech"},
    {"name": "VK", "url": "https://vk.com/{u}", "check": "status", "region": "global"},
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


async def check_platform(client, platform, username):
    """يفحص منصة وحدة."""
    url = platform["url"].format(u=username)
    result = {
        "name": platform["name"],
        "url": url,
        "region": platform["region"],
        "found": False,
        "status": "-",
    }

    try:
        r = await client.get(url, follow_redirects=True, timeout=10)
        result["status"] = r.status_code

        if platform["check"] == "status":
            # نتحقق من وجود كلمات تدل على صفحة 404
            text_l = r.text.lower()
            not_found_signals = [
                "page not found",
                "not found",
                "doesn't exist",
                "does not exist",
                "غير موجود",
                "الصفحة غير متوفرة",
            ]
            is_404_page = any(sig in text_l for sig in not_found_signals)
            result["found"] = r.status_code == 200 and not is_404_page

        elif platform["check"] == "telegram":
            result["found"] = (
                r.status_code == 200 and "tgme_page_title" in r.text
            )
    except Exception as e:
        result["status"] = f"ERR"

    return result


async def scan_all(username):
    """يفحص كل المنصات بالتوازي."""
    async with httpx.AsyncClient(headers=HEADERS) as client:
        tasks = [check_platform(client, p, username) for p in PLATFORMS]
        return await asyncio.gather(*tasks)


async def get_github_details(username):
    """يجيب تفاصيل GitHub."""
    try:
        return await github_api.get_user(username)
    except github_api.GitHubError:
        return None


@click.command()
@click.argument("username")
@click.option("--json-out", is_flag=True, help="إخراج JSON")
@click.option("--only-found", is_flag=True, help="الموجود فقط")
@click.option("--region", default=None,
              help="فلترة: arab, global, tech")
def athar(username, json_out, only_found, region):
    """أثر — ابحث عن username على المنصات العربية والعالمية."""
    u = username.lstrip("@").strip()

    if not u:
        console.print("[red]✗ لازم تكتب username.[/red]")
        raise SystemExit(2)

    # فلترة بالمنطقة
    platforms = PLATFORMS
    if region:
        platforms = [p for p in platforms if p["region"] == region]

    if not json_out:
        console.print(Panel.fit(
            f"[bold]🔍 نبحث عن:[/bold] @{u}\n"
            f"[dim]عبر {len(platforms)} منصة[/dim]",
            title="[red]HALA · أثر[/red]",
            border_style="red",
        ))

    results = asyncio.run(scan_all(u))

    # GitHub details
    gh = asyncio.run(get_github_details(u))

    found = [r for r in results if r["found"]]

    if json_out:
        output = {
            "username": u,
            "found": found,
            "github": gh,
            "total_checked": len(results),
        }
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # تفاصيل GitHub
    if gh:
        gh_info = f"[bold cyan]GitHub Profile:[/bold cyan]\n"
        if gh.get("name"):
            gh_info += f"  الاسم: {gh['name']}\n"
        if gh.get("bio"):
            gh_info += f"  النبذة: {gh['bio']}\n"
        if gh.get("location"):
            gh_info += f"  الموقع: {gh['location']}\n"
        if gh.get("company"):
            gh_info += f"  الشركة: {gh['company']}\n"
        gh_info += f"  Repos: {gh.get('public_repos', 0)}\n"
        gh_info += f"  Followers: {gh.get('followers', 0)}\n"
        if gh.get("created_at"):
            gh_info += f"  عضو من: {gh['created_at'][:10]}"
        console.print(Panel.fit(
            gh_info,
            title="[cyan]معلومات إضافية[/cyan]",
            border_style="cyan",
        ))

    # جدول النتائج
    table = Table(title=f"النتائج ({len(found)}/{len(results)})", show_lines=False)
    table.add_column("المنصة", style="cyan", no_wrap=True)
    table.add_column("المنطقة", style="dim", no_wrap=True)
    table.add_column("الحالة", no_wrap=True)
    table.add_column("الرابط", style="blue", overflow="fold")

    rows = found if only_found else results
    for r in rows:
        status = "[green]✓[/green]" if r["found"] else "[dim]✗[/dim]"
        region_label = {"arab": "🇸🇦", "global": "🌍", "tech": "💻"}.get(r["region"], "")
        table.add_row(r["name"], region_label, status, r["url"])

    console.print(table)

    if found:
        console.print(f"\n[bold green]✓ لقينا @{u} في {len(found)} منصة.[/bold green]")
    else:
        console.print(f"\n[yellow]ما لقينا @{u} في أي منصة.[/yellow]")
