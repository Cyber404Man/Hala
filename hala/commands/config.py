"""hala config — إدارة مفاتيح API والإعدادات"""
import json
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

CONFIG_DIR = Path.home() / ".hala"
CONFIG_FILE = CONFIG_DIR / "config.json"

# المفاتيح المدعومة
SUPPORTED_KEYS = {
    "urlscan_key": {
        "env": "URLSCAN_API_KEY",
        "desc": "مفتاح urlscan.io (مجاني)",
        "url": "https://urlscan.io/user/signup",
    },
    "virustotal_key": {
        "env": "VIRUSTOTAL_API_KEY",
        "desc": "مفتاح VirusTotal (مجاني)",
        "url": "https://www.virustotal.com/gui/join-us",
    },
    "leakcheck_key": {
        "env": "LEAKCHECK_API_KEY",
        "desc": "مفتاح LeakCheck (اختياري)",
        "url": "https://leakcheck.io/pricing",
    },
    "github_token": {
        "env": "GITHUB_TOKEN",
        "desc": "GitHub token (اختياري، يرفع الحد)",
        "url": "https://github.com/settings/tokens",
    },
}


def load_config() -> dict:
    """يحمّل الإعدادات."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        return {}
    with CONFIG_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    """يحفظ الإعدادات."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_key(key_name: str) -> str | None:
    """يجيب مفتاح من config أو env."""
    import os

    if key_name not in SUPPORTED_KEYS:
        return None

    # من config أولاً
    config = load_config()
    if config.get(key_name):
        return config[key_name]

    # من env
    env_name = SUPPORTED_KEYS[key_name]["env"]
    return os.environ.get(env_name)


@click.command()
@click.option("--set", "set_key", nargs=2, metavar="KEY VALUE",
              help="حفظ مفتاح: --set urlscan_key xxx")
@click.option("--get", "get_key_name", metavar="KEY",
              help="عرض مفتاح")
@click.option("--delete", "delete_key", metavar="KEY",
              help="حذف مفتاح")
@click.option("--list", "list_all", is_flag=True,
              help="عرض كل المفاتيح")
@click.option("--path", is_flag=True, help="عرض مسار ملف الإعدادات")
def config(set_key, get_key_name, delete_key, list_all, path):
    """إدارة مفاتيح API والإعدادات."""
    if path:
        console.print(f"[bold]ملف الإعدادات:[/bold] {CONFIG_FILE}")
        return

    if set_key:
        key, value = set_key
        if key not in SUPPORTED_KEYS:
            console.print(f"[red]✗ مفتاح غير مدعوم: {key}[/red]")
            console.print(f"[dim]المفاتيح المتاحة: "
                          f"{', '.join(SUPPORTED_KEYS.keys())}[/dim]")
            raise SystemExit(2)
        cfg = load_config()
        cfg[key] = value
        save_config(cfg)
        console.print(f"[green]✓ تم حفظ {key}[/green]")
        return

    if get_key_name:
        value = get_key(get_key_name)
        if value:
            # نخفي جزء من المفتاح
            masked = value[:6] + "..." + value[-4:] if len(value) > 12 else "***"
            console.print(f"[bold]{get_key_name}:[/bold] {masked}")
        else:
            console.print(f"[yellow]✗ {get_key_name} غير محفوظ[/yellow]")
        return

    if delete_key:
        cfg = load_config()
        if delete_key in cfg:
            del cfg[delete_key]
            save_config(cfg)
            console.print(f"[yellow]✓ تم حذف {delete_key}[/yellow]")
        else:
            console.print(f"[dim]{delete_key} غير موجود[/dim]")
        return

    if list_all:
        cfg = load_config()
        table = Table(title="HALA · الإعدادات", show_lines=True)
        table.add_column("المفتاح", style="cyan")
        table.add_column("الحالة")
        table.add_column("المصدر", style="dim")
        table.add_column("الوصف")

        for key, info in SUPPORTED_KEYS.items():
            if key in cfg:
                status = "[green]✓ محفوظ[/green]"
                source = "config"
            elif get_key(key):
                status = "[yellow]✓ env var[/yellow]"
                source = info["env"]
            else:
                status = "[dim]✗ غير موجود[/dim]"
                source = "-"

            table.add_row(key, status, source, info["desc"])

        console.print(table)
        console.print(f"\n[dim]ملف الإعدادات: {CONFIG_FILE}[/dim]")
        console.print(f"[dim]للحصول على مفتاح: hala config --help[/dim]")
        return

    # عرض افتراضي
    console.print(Panel.fit(
        "[bold]hala config[/bold] — إدارة مفاتيح API\n\n"
        "أمثلة:\n"
        "  [cyan]hala config --list[/cyan]\n"
        "  [cyan]hala config --set urlscan_key YOUR_KEY[/cyan]\n"
        "  [cyan]hala config --get urlscan_key[/cyan]\n"
        "  [cyan]hala config --delete urlscan_key[/cyan]",
        title="[red]HALA · config[/red]",
        border_style="red",
    ))
