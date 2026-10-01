"""hala sitr - ستر: امسح بياناتك من المواقع العربية"""
import webbrowser
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hala.utils import load_json

console = Console()

# خريطة أسماء الدول
COUNTRIES = {
    "PS": "فلسطين",
    "SA": "السعودية",
    "EG": "مصر",
    "YE": "اليمن",
    "JO": "الأردن",
    "AE": "الإمارات",
    "ALL": "الكل",
}


@click.command()
@click.option("--country", default=None,
              help="فلترة حسب الدولة: PS, SA, EG, YE, JO, AE")
@click.option("--open", "open_browser", is_flag=True,
              help="افتح الروابط في المتصفح تلقائيًا")
def sitr(country: str | None, open_browser: bool):
    """ستر - روابط حذف بياناتك من المواقع العربية والعالمية."""
    data = load_json("optout_urls.json")
    sites = data.get("sites", [])

    if country:
        country = country.upper()
        sites = [
            s for s in sites
            if country in s.get("countries", []) or "ALL" in s.get("countries", [])
        ]

    if not sites:
        console.print("[yellow]ما لقينا مواقع لهذه الدولة.[/yellow]")
        return

    # عنوان
    title = "HALA · ستر"
    if country:
        title += f" · {COUNTRIES.get(country, country)}"
    console.print(Panel.fit(
        "[bold]روابط رسمية لحذف بياناتك من المواقع اللي بتفضح رقمك[/bold]\n"
        "[dim]افتح كل رابط واتبع خطوات الحذف[/dim]",
        title=f"[red]{title}[/red]",
        border_style="red",
    ))

    # جدول
    table = Table(show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("الموقع", style="cyan", no_wrap=True)
    table.add_column("الوصف")
    table.add_column("الدول", style="yellow", no_wrap=True)

    for i, s in enumerate(sites, 1):
        countries_str = ", ".join(s.get("countries", []))
        table.add_row(str(i), s["name"], s.get("desc", ""), countries_str)

    console.print(table)

    # فتح المتصفح
    if open_browser:
        console.print("\n[yellow]نفتح الروابط في المتصفح...[/yellow]")
        opened = 0
        for s in sites:
            try:
                webbrowser.open(s["url"])
                opened += 1
            except Exception as e:
                console.print(f"[red]✗ فشل فتح {s['name']}: {e}[/red]")
        console.print(f"[green]✓ فتحنا {opened} رابط.[/green]")
    else:
        console.print(
            f"\n[bold]عندك {len(sites)} موقع.[/bold] "
            "[dim]استخدم --open لفتحهم تلقائيًا، أو انسخ الروابط يدويًا.[/dim]"
        )
