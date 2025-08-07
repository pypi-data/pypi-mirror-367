"""Console script for cctp."""

import logging
import os
import pathlib

import typer
from rich.console import Console

from cctp import __version__

app = typer.Typer()
console = Console()

logging.basicConfig(level=logging.INFO, format="[*] %(message)s")
logger = logging.getLogger(__name__)


@app.command()
def main(
    *,
    offline: bool = typer.Option(None, "--offline", help="Offline mode"),
) -> None:
    """Console script for cctp."""
    console.print(f"cctp v{__version__}")

    if offline:
        cctp_dir = pathlib.Path("~/.cookiecutters/cctp").expanduser()
        if not cctp_dir.is_dir():
            logger.error(
                f"{cctp_dir.parent}目录下未找到cctp, 请下载后解压到该目录",
            )
            return
        os.system("uvx cookiecutter cctp")

    os.system("uvx cookiecutter https://gitee.com/gooker_young/cctp.git")


if __name__ == "__main__":
    app()
