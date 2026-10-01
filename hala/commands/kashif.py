"""hala kashif — كاشف: هل إيميلي أو رقمي مسرّب؟"""
import asyncio
import json
import click
import phonenumbers
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hala.sources import xposedornot, leakcheck

console = Console()


def detect_type(target: str) -> str:
    """يميز بين إيميل ورقم هاتف."""
    if "@" in target and "." in target:
        return "email"
    return "phone"


def normalize_phone(raw: str, region: str = "PS") -> str | None:
    """يحوّل الرقم لصيغة E.164."""
    try:
        p = phonenumbers.parse(raw, region)
        if not phonenumbers.is_valid_number(p):
            return None
        return phonenumbers.format_number(
            p, phonenumbers.PhoneNumberFormat.E164
        )
    except phonenumbers.NumberParseException:
        return None


async def scan_email(email: str) -> list[dict]:
    """يفحص إيميل في كل المصادر المجانية."""
    results = []

    # XposedOrNot
    try:
        results.extend(await xposedornot.check_email(email))
    except xposedornot.XposedError as e:
        console.print(f"[dim]⚠ XposedOrNot: {e}[/dim]")

    # LeakCheck
    try:
        results.extend(await leakcheck.check(email))
    except leakcheck.LeakCheckError as e:
        console.print(f"[dim]⚠ LeakCheck: {e}[/dim]")

    return results


async def scan_phone(e164: str) -> list[dict]:
    """يفحص رقم في المصادر المتاحة."""
    results = []

    try:
        results.extend(await leakcheck.check(e164))
    except leakcheck.LeakCheckError as e:
        console.print(f"[dim]⚠ LeakCheck: {e}[/dim]")

    return results


@click.command()
@click.argument("target")
@click.option("--region", default="PS", help="PS, SA, EG, YE, JO...")
@click.option("--json-out", is_flag=True, help="إخراج JSON")
def kashif(target: str, region: str, json_out: bool):
    """كاشف — افحص إيميل أو رقم هاتف في تسريبات معروفة."""
    target_type = detect_type(target)

    if target_type == "email":
        email = target.lower().strip()
        if not json_out:
            console.print(Panel.fit(
                f"[bold]الإيميل:[/bold] {email}\n"
                f"[bold]المصادر:[/bold] XposedOrNot, LeakCheck",
                title="[red]HALA · كاشف[/red]",
                border_style="red",
            ))
        hits = asyncio.run(scan_email(email))
        out_target = email
    else:
        e164 = normalize_phone(target, region)
        if not e164:
            console.print("[red]✗ رقم غير صالح.[/red]")
            console.print("[dim]مثال: hala kashif 0599123456 --region PS[/dim]")
            raise SystemExit(2)
        if not json_out:
            console.print(Panel.fit(
                f"[bold]الرقم:[/bold] {e164}\n"
                f"[bold]المصادر:[/bold] LeakCheck",
                title="[red]HALA · كاشف[/red]",
                border_style="red",
            ))
        hits = asyncio.run(scan_phone(e164))
        out_target = e164

    if json_out:
        click.echo(json.dumps(
            {"target": out_target, "type": target_type, "hits": hits},
            ensure_ascii=False, indent=2,
        ))
        return

    if not hits:
        console.print("[green]✓ ما لقينا تسريبات معروفة.[/green]")
        console.print("[dim]ملاحظة: غياب الدليل ≠ دليل على الغياب.[/dim]")
        return

    # إزالة التكرار (نفس التسريب من مصدرين)
    seen = set()
    unique = []
    for h in hits:
        key = (h.get("name") or h.get("title") or "").lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(h)

    table = Table(
        title=f"⚠ لقينا {len(unique)} تسريب",
        show_lines=True,
    )
    table.add_column("المصدر", style="dim", no_wrap=True)
    table.add_column("التسريب", style="cyan")
    table.add_column("التاريخ", style="yellow")
    table.add_column("الحجم", style="magenta")

    for h in unique:
        records = h.get("records")
        records_str = f"{records:,}" if isinstance(records, int) else "-"

        table.add_row(
            h.get("source", "?"),
            str(h.get("title") or h.get("name") or "-"),
            str(h.get("date") or "-"),
            records_str,
        )

    console.print(table)
    console.print(f"\n[red]⚠ ظهر الهدف في {len(unique)} تسريب![/red]")
    console.print("[bold]ننصحك:[/bold]")
    console.print("  1. غيّر كلمات السر")
    console.print("  2. فعّل 2FA")
    console.print("  3. راقب حسابك")
