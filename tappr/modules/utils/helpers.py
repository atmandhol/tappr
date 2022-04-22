import re
import subprocess

from tappr.modules.utils import logger
from tappr.modules.utils.ui import UI

typer_logger = logger.TyperLogger()


class SubProcessHelpers:
    @staticmethod
    def run_proc(cmd):
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        process.wait()
        return process, out, err

    def run_pre_req(self, cmd, tool):
        process, out, err = self.run_proc(cmd)
        ver = ""
        if out:
            ver = re.search(r"([\d.]+)", out.decode()).group(1)
            if ver == ".":
                ver = " "
            else:
                ver = " " + ver + " "

        if process.returncode != 0:
            typer_logger.msg(f":red_apple: [red]{tool}[/red] not found", bold=True)
            return False
        typer_logger.msg(f":green_apple: {tool}[green]{ver}[/green]installed")
        return True


class PivnetHelpers:
    def __init__(self):
        self.subprocess_helpers = SubProcessHelpers()
        self.ui_helpers = UI(subprocess_helper=self.subprocess_helpers, logger=typer_logger)

    def download(self, product_slug: str, release_version: str, product_file_id: str, download_dir: str, state: dict):
        """
        Download product files from pivnet.

        """
        cmd = f"pivnet download-product-files --product-slug='{product_slug}' --release-version='{release_version}' --product-file-id={product_file_id} --download-dir='{download_dir}' --accept-eula"
        typer_logger.msg(f":arrow_double_down: Download [yellow]{product_slug}[/yellow].", bold=True)
        proc, _, _ = self.ui_helpers.progress(cmd=cmd, state=state, message="Downloading")
        if proc.returncode == 0:
            typer_logger.msg(f":package: {product_slug} downloaded [green]successfully[/green]")
        else:
            typer_logger.msg(f":broken_heart: Unable to download {product_slug}. Use [bold]--verbose[/bold] flag for error details.")
        return proc.returncode

    def login(self, api_token: str, state: dict):
        """
        Login to pivnet.

        """
        cmd = f"pivnet login --api-token='{api_token}'"
        typer_logger.msg(f":key: Log into [yellow]Pivnet[/yellow].", bold=True)
        proc, _, _ = self.ui_helpers.progress(cmd=cmd, state=state, message="Logging in")
        if proc.returncode == 0:
            typer_logger.msg(f":rocket: Login [green]successful[/green]")
        else:
            typer_logger.msg(f":broken_heart: Unable to Login. Use [bold]--verbose[/bold] flag for error details.")
        return proc.returncode
