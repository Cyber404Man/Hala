"""hala sitr — ستر: امسح بياناتك + تابع تقدمك"""
import webbrowser
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hala.utils import (
    load_json, load_state, mark_completed,
    mark_pending, reset_state,
)

console = Console()

COUNTRIES = {
    "PS": "فلسطين", "SA": "السعودية", "EG": "مصر", "YE": "اليمن",
    "JO": "الأردن", "AE": "الإمارات", "ALL": "الكل",
}

TYPES = {
    "people_search": "بحث أشخاص",
    "social": "شبكات اجتماعية",
    "marketplace": "أسواق",
    "marketing": "تسويق بيانات",
    "search_engine": "محركات بحث",
    "breach_check": "فحص تسريبات",
}

DIFFICULTY = {
    "easy": "🟢 سهل",
    "medium": "🟡 متوسط",
    "hard": "🔴 صعب",
}


def get_sites(country=None, site_type=None):
    """يجيب المواقع مع الفلترة."""
    data = load_json("optout_urls.json")
    sites = data.get("sites", [])

    if country:
        country = country.upper()
        sites = [
            s for s in sites
            if country in s.get("countries", [])
            or "ALL" in s.get("countries", [])
        ]

    if site_type:
        sites = [s for s in sites if s.get("type") == site_type]

    return sites


@click.command()
@click.option("--country", default=None, help="PS, SA, EG, YE, JO, AE")
@click.option("--type", "site_type", default=None,
              help="people_search, social, marketplace, marketing, search_engine, breach_check")
@click.option("--open", "open_browser", is_flag=True,
              help="افتح الروابط في المتصفح")
@click.option("--mark", "mark_id", default=None,
              help="علّم موقع كمكتمل: --mark truecaller")
@click.option("--unmark", "unmark_id", default=None,
              help="شيل علامة موقع")
@click.option("--status", is_flag=True, help="اعرض حالة تقدمك")
@click.option("--reset", is_flag=True, help="صفّر كل الحالة")
@click.option("--json-out", is_flag=True)
def sitr(country, site_type, open_browser, mark_id, unmark_id,
         status, reset, json_out):
    """ستر — امسح بياناتك من مواقع تجميع البيانات + تابع تقدمك."""
    # reset
    if reset:
        reset_state()
        console.print("[green]✓ تم تصفير الحالة.[/green]")
        return

    # mark complete
    if mark_id:
        mark_completed(mark_id)
        console.print(f"[green]✓ علّمت {mark_id} كمكتمل.[/green]")
        return

    # unmark
    if unmark_id:
        mark_pending(unmark_id)
        console.print(f"[yellow]✓ شلت علامة {unmark_id}.[/yellow]")
        return

    # status only
    if status:
        state = load_state()
        completed = state.get("completed", [])
        data = load_json("optout_urls.json")
        total = len(data.get("sites", []))

        console.print(Panel.fit(
            f"[bold]التقدم:[/bold] {len(completed)} / {total} موقع\n"
            f"[bold]النسبة:[/bold] "
            f"{int(len(completed) / total * 100) if total else 0}%",
            title="[red]HALA · ستر — حالة التقدم[/red]",
            border_style="red",
        ))

        if completed:
            console.print("\n[bold]المواقع المكتملة:[/bold]")
            for site_id in completed:
                site = next((s for s in data["sites"] if s["id"] == site_id), None)
                if site:
                    console.print(f"  [green]✓[/green] {site['name']}")
        return

    # main list
    sites = get_sites(country, site_type)

    if not sites:
        console.print("[yellow]ما لقينا مواقع بهذي الفلترة.[/yellow]")
        return

    state = load_state()
    completed = state.get("completed", [])

    title = "HALA · ستر"
    if country:
        title += f" · {COUNTRIES.get(country, country)}"
    if site_type:
        title += f" · {TYPES.get(site_type, site_type)}"

    console.print(Panel.fit(
        f"[bold]عدد المواقع:[/bold] {len(sites)}\n"
        f"[bold]مكتملة:[/bold] {sum(1 for s in sites if s['id'] in completed)}",
        title=f"[red]{title}[/red]",
        border_style="red",
    ))

    if json_out:
        import json
        click.echo(json.dumps(sites, ensure_ascii=False, indent=2))
        return

    # جدول
    table = Table(show_lines=False)
    table.add_column("✓", style="green", width=3)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("الموقع", style="cyan", no_wrap=True)
    table.add_column("النوع", style="yellow", no_wrap=True)
    table.add_column("الصعوبة", no_wrap=True)
    table.add_column("الرابط", style="blue", overflow="fold")

    for s in sites:
        check = "✓" if s["id"] in completed else ""
        table.add_row(
            check,
            s["id"],
            s["name"],
            TYPES.get(s.get("type"), "-"),
            DIFFICULTY.get(s.get("difficulty"), "-"),
            s["url"],
        )

    console.print(table)

    # تعليمات
    console.print("\n[bold]كيف تستخدم:[/bold]")
    console.print(f"  • [dim]افتح الروابط يدويًا، أو استخدم --open[/dim]")
    console.print(f"  • [dim]بعد ما تحذف بياناتك من موقع: hala sitr --mark <id>[/dim]")
    console.print(f"  • [dim]شوف تقدمك: hala sitr --status[/dim]")

    # فتح المتصفح
    if open_browser:
        console.print("\n[yellow]نفتح الروابط في المتصفح...[/yellow]")
        opened = 0
        for s in sites:
            try:
                webbrowser.open(s["url"])
                opened += 1
            except Exception:
                pass
        console.print(f"[green]✓ فتحنا {opened} رابط.[/green]")
