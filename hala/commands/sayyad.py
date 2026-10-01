"""hala sayyad - صياد: توليد domains تصيّد محتملة على براند عربي"""
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# خرائط تهجئة عربية -> إنجليزي
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

# نهايات نطاقات مشبوهة + رسمية
SUSPICIOUS_TLDS = ["-ps.com", "-sa.com", "-eg.com", "-online.com", "-secure.com"]
COMMON_TLDS = [".com", ".net", ".ps", ".sa", ".eg", ".jo", ".ye", ".ly", ".co"]


def generate_variants(brand: str) -> set[str]:
    """يولّد أشكال كتابة محتملة للبراند."""
    brand = brand.strip().lower()
    variants = {brand}

    # إزالة الشرطات والمسافات
    variants.add(brand.replace("-", "").replace(" ", ""))
    variants.add(brand.replace("_", ""))

    # مضاعفة الحروف (jawal -> jawwal)
    for i, c in enumerate(brand):
        if c.isalpha():
            variants.add(brand[: i + 1] + c + brand[i + 1:])

    # لو عربي -> ترجم
    if brand in TRANSLIT:
        variants.update(TRANSLIT[brand])

    # لو إنجليزي -> دوّر العربي
    for ar, en_list in TRANSLIT.items():
        if brand in en_list:
            variants.add(ar.replace(" ", ""))
            variants.update(en_list)

    # نظّف
    return {v for v in variants if v and len(v) >= 3}


@click.command()
@click.option("--brand", required=True, help="اسم البراند (عربي أو إنجليزي)")
@click.option("--dialect", default="ps", help="ps, sa, eg, ye, jo (للسياق)")
@click.option("--top", default=30, help="عدد النتائج الأقصى")
@click.option("--suspicious-only", is_flag=True,
              help="اعرض النطاقات المشبوهة فقط")
def sayyad(brand: str, dialect: str, top: int, suspicious_only: bool):
    """صياد - يولّد domains تصيّد محتملة على براند عربي."""
    variants = generate_variants(brand)

    if not variants:
        console.print("[red]✗ ما قدرنا نولّد variants.[/red]")
        raise SystemExit(2)

    # ولّد المرشحين
    candidates = []
    tlds = SUSPICIOUS_TLDS if suspicious_only else COMMON_TLDS + SUSPICIOUS_TLDS

    for v in sorted(variants):
        for tld in tlds:
            candidates.append(f"{v}{tld}")

    # إزالة التكرار
    candidates = list(dict.fromkeys(candidates))[:top]

    console.print(Panel.fit(
        f"[bold]البراند:[/bold] {brand}\n"
        f"[bold]اللهجة:[/bold] {dialect}\n"
        f"[bold]عدد الـvariants:[/bold] {len(variants)}\n"
        f"[bold]عدد النطاقات:[/bold] {len(candidates)}",
        title="[red]HALA · صياد[/red]",
        border_style="red",
    ))

    table = Table(show_lines=False)
    table.add_column("#", style="dim", width=3)
    table.add_column("Domain محتمل", style="red")
    table.add_column("نوع", style="yellow")

    for i, c in enumerate(candidates, 1):
        is_suspicious = any(c.endswith(t) for t in SUSPICIOUS_TLDS)
        kind = "⚠ مشبوه" if is_suspicious else "عادي"
        table.add_row(str(i), c, kind)

    console.print(table)
    console.print(
        "\n[dim]استخدم urlscan.io أو VirusTotal للتحقق إن كان أحدهم نشطًا.[/dim]"
    )
    console.print(
        "[dim]هذه الأداة تولّد احتمالات فقط — التحقق مسؤوليتك.[/dim]"
    )
