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
            typer_logger.msg(f":red_apple: [red]{tool}[/red] not found", bold=False)
            return False
        typer_logger.msg(f":green_apple: {tool}[green]{ver}[/green]installed")
        return True
