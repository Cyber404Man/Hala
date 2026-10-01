
"""hala nlp — كشف الاحتيال في الرسائل العربية + لهجات + استخراج كيانات"""
import re
import json
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hala.utils import load_json

console = Console()

# regex لاستخراج الروابط والأرقام
URL_PATTERN = re.compile(
    r"(https?://[^\s<>\"']+|www\.[^\s<>\"']+|[a-z0-9-]+\.(?:com|net|org|xyz|top|tk|ml|ga|cf|online|site)(?:/[^\s]*)?)",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(
    r"(\+?\d[\d\s\-()]{7,}\d)"
)


def detect_dialect(text: str) -> list[tuple[str, int]]:
    """يكشف لهجة النص. يرجع قائمة (dialect_code, score) مرتبة."""
    dialects = load_json("dialects.json")
    text_l = text.lower()
    scores = []

    for code, data in dialects.items():
        score = 0
        for marker in data.get("markers", []):
            if marker.lower() in text_l:
                score += 1
        if score > 0:
            scores.append((code, score, data.get("name_ar", code)))

    scores.sort(key=lambda x: -x[1])
    return scores


def extract_urls(text: str) -> list[str]:
    """يستخرج الروابط من النص."""
    return list(set(URL_PATTERN.findall(text)))


def extract_phones(text: str) -> list[str]:
    """يستخرج الأرقام من النص."""
    found = PHONE_PATTERN.findall(text)
    return list(set(f.strip() for f in found))


def analyze(text: str) -> dict:
    """يحلل نص عربي بالكامل."""
    patterns = load_json("scam_patterns.json")
    text_l = text.lower()

    hits = []  # (category, indicator, weight, explain)
    score = 0

    # regex patterns
    for rx in patterns.get("_regex", []):
        if re.search(rx["pattern"], text, re.IGNORECASE):
            hits.append((
                rx["name"],
                rx["pattern"][:50],
                rx.get("weight", 20),
                rx.get("explain", ""),
            ))
            score += rx.get("weight", 20)

    # keyword categories
    for category, data in patterns.items():
        if category.startswith("_"):
            continue
        if not isinstance(data, dict):
            continue
        weight = data.get("weight", 10)
        matched = []
        for kw in data.get("keywords", []):
            if kw.lower() in text_l:
                matched.append(kw)
        if matched:
            hits.append((
                category,
                ", ".join(matched[:3]),
                weight,
                f"{len(matched)} مؤشر",
            ))
            score += weight * min(len(matched), 3)  # cap

    score = min(score, 100)

    if score >= 60:
        verdict = "SCAM"
    elif score >= 30:
        verdict = "SUSPICIOUS"
    else:
        verdict = "CLEAN"

    return {
        "score": score,
        "verdict": verdict,
        "hits": hits,
        "dialects": detect_dialect(text),
        "urls": extract_urls(text),
        "phones": extract_phones(text),
    }


def verdict_color(v: str) -> str:
    return {"SCAM": "red", "SUSPICIOUS": "yellow", "CLEAN": "green"}[v]


def verdict_bilingual(v: str) -> str:
    return {
        "SCAM": "SCAM · احتيال مؤكد",
        "SUSPICIOUS": "SUSPICIOUS · مشبوه",
        "CLEAN": "CLEAN · سليم",
    }[v]


@click.command()
@click.option("--text", required=True, help="النص للتحليل")
@click.option("--json-out", is_flag=True, help="إخراج JSON")
@click.option("--explain", is_flag=True, help="شرح مفصّل")
def nlp(text: str, json_out: bool, explain: bool):
    """تحليل رسالة عربية — احتيال؟ لهجة؟ روابط؟"""
    result = analyze(text)

    if json_out:
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return

    color = verdict_color(result["verdict"])

    # panel رئيسي
    panel_text = f"[bold]النص:[/bold]\n{text}\n\n"
    panel_text += (
        f"[bold {color}]الحكم: {verdict_bilingual(result['verdict'])} "
        f"({result['score']}/100)[/bold {color}]"
    )

    console.print(Panel.fit(
        panel_text,
        title="[red]HALA · NLP[/red]",
        border_style="red",
    ))

    # اللهجة
    if result["dialects"]:
        top = result["dialects"][0]
        console.print(
            f"\n[bold]اللهجة المكتشفة:[/bold] "
            f"[cyan]{top[2]}[/cyan] ({top[0]}) — {top[1]} مؤشر"
        )
        if len(result["dialects"]) > 1 and explain:
            others = ", ".join(
                f"{d[2]} ({d[1]})" for d in result["dialects"][1:3]
            )
            console.print(f"[dim]لهجات ثانية محتملة: {others}[/dim]")

    # الروابط
    if result["urls"]:
        console.print("\n[bold]🔗 الروابط المكتشفة:[/bold]")
        for u in result["urls"][:5]:
            console.print(f"  [blue]{u}[/blue]")

    # الأرقام
    if result["phones"]:
        console.print("\n[bold]📞 الأرقام المكتشفة:[/bold]")
        for p in result["phones"][:5]:
            console.print(f"  [yellow]{p}[/yellow]")

    # المؤشرات
    if result["hits"]:
        table = Table(title="المؤشرات المكتشفة", show_lines=True)
        table.add_column("الفئة", style="cyan", no_wrap=True)
        table.add_column("المؤشر")
        table.add_column("الوزن", style="yellow")
        if explain:
            table.add_column("التفسير", style="dim")

        for h in result["hits"]:
            cat, kw, weight, expl = h
            row = [cat, kw[:40], str(weight)]
            if explain:
                row.append(expl or "-")
            table.add_row(*row)

        console.print(table)
    else:
        console.print("\n[green]ما لقينا مؤشرات احتيال واضحة.[/green]")
