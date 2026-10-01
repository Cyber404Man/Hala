"""hala sayyad — صياد: توليد + فحص نطاقات تصيّد محتملة"""
import asyncio
import click
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hala.sources import urlscan

console = Console()

TRANSLIT = {
    "جوال": ["jawwal", "jawal", "jawaal", "jwwal"],
    "زين": ["zain", "zine", "zayn"],
    "اوريدو": ["ooredoo", "oredoo", "orido"],
    "اتصالات": ["etisalat", "etisalt"],
    "فودافون": ["vodafone", "vodafon"],
    "بنك": ["bank", "bnk"],
    "فلسطين": ["palestine", "palestin", "filasteen"],
    "الراجحي": ["alrajhi", "rajhi", "al-rajhi"],
    "الأهلي": ["ahli", "al-ahli", "alahli"],
    "البنك العربي": ["arabbank", "arab-bank", "alarabibank"],
}

SUSPICIOUS_TLDS = [
    "-ps.com", "-sa.com", "-eg.com", "-online.com", "-secure.com",
]
COMMON_TLDS = [".com", ".net", ".ps", ".sa", ".eg", ".jo", ".ye", ".co"]


def generate_variants(brand: str) -> set[str]:
    """يولّد أشكال كتابة محتملة."""
    brand = brand.strip().lower()
    variants = {brand}
    variants.add(brand.replace("-", "").replace(" ", ""))
    variants.add(brand.replace("_", ""))

    for i, c in enumerate(brand):
        if c.isalpha():
            variants.add(brand[: i + 1] + c + brand[i + 1:])

    if brand in TRANSLIT:
        variants.update(TRANSLIT[brand])

    for ar, en_list in TRANSLIT.items():
        if brand in en_list:
            variants.add(ar.replace(" ", ""))
            variants.update(en_list)

    return {v for v in variants if v and len(v) >= 3}


async def dns_check(domain: str) -> bool:
    """يفحص إذا النطاق له DNS record (يعني مسجّل)."""
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(
                f"https://dns.google/resolve?name={domain}&type=A"
            )
            data = r.json()
            return data.get("Status") == 0 and bool(data.get("Answer"))
    except Exception:
        return False


async def check_all_dns(domains: list[str]) -> dict[str, bool]:
    """يفحص DNS لكل النطاقات بالتوازي."""
    tasks = [dns_check(d) for d in domains]
    results = await asyncio.gather(*tasks)
    return dict(zip(domains, results))


@click.command()
@click.option("--brand", required=True, help="اسم البراند")
@click.option("--dialect", default="ps", help="ps, sa, eg, ye, jo")
@click.option("--top", default=20, help="عدد النتائج الأقصى")
@click.option("--suspicious-only", is_flag=True,
              help="النطاقات المشبوهة فقط")
@click.option("--check-dns", is_flag=True,
              help="افحص إذا النطاقات مسجّلة فعلاً (DNS)")
@click.option("--scan", "do_scan", is_flag=True,
              help="افحص النطاقات المسجّلة في urlscan")
@click.option("--urlscan-key", envvar="URLSCAN_API_KEY", default=None,
              help="مفتاح urlscan.io")
def sayyad(brand, dialect, top, suspicious_only, check_dns, do_scan, urlscan_key):
    """صياد — يولّد ويفحص نطاقات تصيّد محتملة على براند عربي."""
    variants = generate_variants(brand)

    if not variants:
        console.print("[red]✗ ما قدرنا نولّد variants.[/red]")
        raise SystemExit(2)

    candidates = []
    tlds = SUSPICIOUS_TLDS if suspicious_only else COMMON_TLDS + SUSPICIOUS_TLDS
    for v in sorted(variants):
        for tld in tlds:
            candidates.append(f"{v}{tld}")

    candidates = list(dict.fromkeys(candidates))[:top]

    console.print(Panel.fit(
        f"[bold]البراند:[/bold] {brand}\n"
        f"[bold]اللهجة:[/bold] {dialect}\n"
        f"[bold]عدد النطاقات:[/bold] {len(candidates)}",
        title="[red]HALA · صياد[/red]",
        border_style="red",
    ))

    # فحص DNS
    dns_results = {}
    if check_dns or do_scan:
        console.print("[dim]🔍 نفحص DNS...[/dim]")
        dns_results = asyncio.run(check_all_dns(candidates))

    # جدول
    table = Table(show_lines=False)
    table.add_column("#", style="dim", width=3)
    table.add_column("Domain", style="red")
    table.add_column("نوع", style="yellow")

    if check_dns or do_scan:
        table.add_column("DNS", style="cyan")

    for i, c in enumerate(candidates, 1):
        is_suspicious = any(c.endswith(t) for t in SUSPICIOUS_TLDS)
        kind = "⚠ مشبوه" if is_suspicious else "عادي"
        row = [str(i), c, kind]
        if check_dns or do_scan:
            dns_status = "[green]مسجّل[/green]" if dns_results.get(c) else "[dim]غير مسجّل[/dim]"
            row.append(dns_status)
        table.add_row(*row)

    console.print(table)

    # urlscan
    if do_scan and urlscan_key:
        live_domains = [d for d, found in dns_results.items() if found]
        if not live_domains:
            console.print("\n[green]✓ ما في نطاقات مسجّلة — ممتاز![/green]")
            return

        console.print(f"\n[dim]🔍 نفحص {len(live_domains)} نطاق في urlscan...[/dim]")
        found_scans = []
        for domain in live_domains:
            try:
                result = asyncio.run(urlscan.check_if_live(domain, urlscan_key))
                if result:
                    found_scans.append(result)
            except urlscan.UrlscanError as e:
                console.print(f"[dim]⚠ urlscan: {e}[/dim]")
                break

        if not found_scans:
            console.print("[green]✓ ما في scans سابقة لهذي النطاقات.[/green]")
            return

        scan_table = Table(title="⚠ نطاقات نشطة في urlscan", show_lines=True)
        scan_table.add_column("Domain", style="red")
        scan_table.add_column("IP", style="cyan")
        scan_table.add_column("الدولة", style="yellow")
        scan_table.add_column("السيرفر")
        scan_table.add_column("تاريخ الفحص", style="dim")

        for s in found_scans:
            scan_table.add_row(
                str(s.get("domain") or "-"),
                str(s.get("ip") or "-"),
                str(s.get("country") or "-"),
                str(s.get("server") or "-"),
                str(s.get("scan_date") or "-")[:10],
            )

        console.print(scan_table)
        console.print(f"\n[red]⚠ {len(found_scans)} نطاق نشط![/red]")
        console.print("[dim]راجعهم يدويًا في urlscan.io[/dim]")
