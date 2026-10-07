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
from hala.commands import sitr  # noqa: E402
from hala.commands import athar, sayyad, nlp  # noqa: E402
from hala.commands import config  # noqa: E402
main.add_command(config.config)
main.add_command(athar.athar)
main.add_command(kashif.kashif)
main.add_command(sitr.sitr)
main.add_command(sayyad.sayyad)
main.add_command(nlp.nlp)
if __name__ == "__main__":
    main()
