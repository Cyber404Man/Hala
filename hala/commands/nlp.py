"""hala nlp - كشف الرسائل الاحتيالية العربية (rule-based v1)"""
import re
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hala.utils import load_json

console = Console()


def analyze(text: str) -> dict:
    """يحلل نص عربي ويكشف مؤشرات الاحتيال."""
    patterns = load_json("scam_patterns.json")
    text_l = text.lower()

    hits: list[tuple[str, str, int]] = []
    score = 0

    # فحص الـregex
    for rx in patterns.get("_regex", []):
        if re.search(rx["pattern"], text, re.IGNORECASE):
            hits.append((rx["name"], f"regex: {rx['pattern'][:40]}...", rx.get("weight", 20)))
            score += rx.get("weight", 20)

    # فحص الكلمات المفتاحية
    for category, data in patterns.items():
        if category.startswith("_"):
            continue
        if not isinstance(data, dict):
            continue
        weight = data.get("weight", 10)
        for kw in data.get("keywords", []):
            if kw.lower() in text_l:
                hits.append((category, kw, weight))
                score += weight

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
    }


def verdict_color(v: str) -> str:
    return {"SCAM": "red", "SUSPICIOUS": "yellow", "CLEAN": "green"}[v]


def verdict_arabic(v: str) -> str:
    return {
        "SCAM": "احتيال مؤكد",
        "SUSPICIOUS": "مشبوه",
        "CLEAN": "سليم",
    }[v]


@click.command()
@click.option("--text", required=True, help="النص للتحليل")
def nlp(text: str):
    """تحليل رسالة عربية - هل هي احتيال؟"""
    result = analyze(text)
    color = verdict_color(result["verdict"])

    console.print(Panel.fit(
        f"[bold]النص:[/bold]\n{text}\n\n"
        f"[bold {color}]الحكم: {verdict_arabic(result['verdict'])} "
        f"({result['score']}/100)[/bold {color}]",
        title="[red]HALA · NLP[/red]",
        border_style="red",
    ))

    if result["hits"]:
        table = Table(title="المؤشرات المكتشفة", show_lines=True)
        table.add_column("النوع", style="cyan")
        table.add_column("المؤشر")
        table.add_column("الوزن", style="yellow")

        for cat, kw, weight in result["hits"]:
            table.add_row(cat, kw, str(weight))

        console.print(table)
    else:
        console.print("[green]ما لقينا مؤشرات احتيال واضحة.[/green]")
