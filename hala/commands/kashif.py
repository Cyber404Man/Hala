"""hala kashif - كاشف: هل رقمي مسرّب؟"""
import json
import asyncio
import click
import httpx
import phonenumbers
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hala.utils import load_json

console = Console()

SOURCES = {
    "ps_daleel": "أدلة هواتف فلسطينية",
    "ye_telecom": "تسريبات اتصالات يمنية",
    "sa_telecom": "تسريبات اتصالات سعودية",
    "eg_delivery": "تسريبات تطبيقات توصيل مصرية",
    "jo_telecom": "تسريبات اتصالات أردنية",
    "hibp": "HaveIBeenPwned",
}


def normalize(raw: str, region: str = "PS") -> str | None:
    """يحوّل الرقم لصيغة E.164 الدولية."""
    try:
        p = phonenumbers.parse(raw, region)
        if not phonenumbers.is_valid_number(p):
            return None
        return phonenumbers.format_number(
            p, phonenumbers.PhoneNumberFormat.E164
        )
    except phonenumbers.NumberParseException:
        return None


def check_community(e164: str) -> list[dict]:
    """يفحص الرقم في قاعدة metadata المجتمعية."""
    db = load_json("arab_leaks_meta.json")
    hits = []
    for leak in db.get("leaks", []):
        prefix = leak.get("prefix", "")
        if prefix and e164.startswith(prefix):
            hits.append(leak)
    return hits


async def check_hibp(e164: str, api_key: str | None) -> list[dict]:
    """يفحص الرقم في HaveIBeenPwned عبر API رسمي."""
    if not api_key:
        return []
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{e164}"
    headers = {"hibp-api-key": api_key, "user-agent": "HALA-CLI"}
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(url, headers=headers)
            if r.status_code != 200:
                return []
            return [
                {
                    "source": "hibp",
                    "name": b.get("Name"),
                    "date": b.get("BreachDate"),
                    "records": b.get("PwnCount"),
                }
                for b in r.json()
            ]
    except Exception:
        return []


@click.command()
@click.argument("phone")
@click.option("--region", default="PS", help="PS, SA, EG, YE, JO...")
@click.option("--hibp-key", envvar="HIBP_API_KEY", default=None,
              help="مفتاح HaveIBeenPwned (اختياري)")
@click.option("--json-out", is_flag=True, help="إخراج JSON للاستخدام البرمجي")
def kashif(phone: str, region: str, hibp_key: str | None, json_out: bool):
    """كاشف - يفحص رقم هاتف عربي في تسريبات معروفة."""
    e164 = normalize(phone, region)
    if not e164:
        console.print("[red]✗ رقم غير صالح.[/red]")
        console.print("[dim]مثال: hala kashif 0599123456 --region PS[/dim]")
        raise SystemExit(2)

    if not json_out:
        console.print(Panel.fit(
            f"[bold]الرقم:[/bold] {e164}\n"
            f"[bold]الدولة:[/bold] {region}",
            title="[red]HALA · كاشف[/red]",
            border_style="red",
        ))

    # جمع النتائج
    hits = check_community(e164)
    hits += asyncio.run(check_hibp(e164, hibp_key))

    if json_out:
        click.echo(json.dumps(
            {"phone": e164, "region": region, "hits": hits},
            ensure_ascii=False, indent=2,
        ))
        return

    if not hits:
        console.print("[green]✓ ما لقينا الرقم في تسريبات معروفة.[/green]")
        console.print("[dim]ملاحظة: غياب الدليل مش دليل على الغياب.[/dim]")
        return

    table = Table(title="⚠ نتائج الكشف", show_lines=True)
    table.add_column("المصدر", style="cyan")
    table.add_column("الوصف")
    table.add_column("التاريخ", style="yellow")
    table.add_column("السجلات", style="magenta")

    for h in hits:
        src = h.get("source", "?")
        table.add_row(
            src,
            SOURCES.get(src, h.get("name", "-")),
            str(h.get("date", "-")),
            f"{h.get('records', 0):,}" if h.get("records") else "-",
        )

    console.print(table)
    console.print(f"\n[red]⚠ الرقم ظهر في {len(hits)} تسريب.[/red]")
    console.print("[dim]ننصح بتغيير كلمات المرور وتفعيل 2FA.[/dim]")
