"""HALA CLI - نقطة الدخول الرئيسية"""
import click
from rich.console import Console

console = Console()

BANNER = r"""
[bold red]
  ██╗  ██╗ █████╗ ██╗      █████╗
  ██║  ██║██╔══██╗██║     ██╔══██╗
  ███████║███████║██║     ███████║
  ██╔══██║██╔══██║██║     ██╔══██║
  ██║  ██║██║  ██║███████╗██║  ██║
  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
[/bold red]
[dim]Hunting Arab Leaks & Assets · v0.1.0[/dim]
[dim]أول إطار عربي لاستخبارات التهديدات[/dim]
"""


@click.group()
@click.version_option("0.1.0", prog_name="hala")
@click.pass_context
def main(ctx):
    """HALA - أداة عربية لاستخبارات التهديدات وحماية الخصوصية."""
    if ctx.invoked_subcommand is None:
        console.print(BANNER)
        console.print(ctx.get_help())

from hala.commands import kashif
main.add_command(kashif.kashif)

if __name__ == "__main__":
    main()
