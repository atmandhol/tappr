from rich import print
from rich.prompt import Confirm, Prompt

from datetime import datetime


class TyperLogger:
    @staticmethod
    def debug(message, bold=True):
        if bold:
            print(f"[white]\[{datetime.now().strftime('%H:%M:%S')}][/white] [bold][yellow]{message}[/yellow][/bold]")
        else:
            print(f"[white]\[{datetime.now().strftime('%H:%M:%S')}][/white] [yellow]{message}[/yellow]")

    @staticmethod
    def error(message, bold=True):
        if bold:
            print(f"[white]\[{datetime.now().strftime('%H:%M:%S')}][/white] [bold][red]{message}[/red][/bold]")
        else:
            print(f"[white]\[{datetime.now().strftime('%H:%M:%S')}][/white] [red]{message}[/red]")

    @staticmethod
    def success(message, bold=True):
        if bold:
            print(f"[white]\[{datetime.now().strftime('%H:%M:%S')}][/white] [bold][green]{message}[/green][/bold]")
        else:
            print(f"[white]\[{datetime.now().strftime('%H:%M:%S')}][/white] [green]{message}[/green]")

    @staticmethod
    def msg(message, bold=False):
        if bold:
            print(f"[#5F9EA0]\[{datetime.now().strftime('%H:%M:%S')}][/#5F9EA0] [bold]{message}[/bold]")
        else:
            print(f"[#5F9EA0]\[{datetime.now().strftime('%H:%M:%S')}][/#5F9EA0] {message}")

    @staticmethod
    def important(message, bold=True):
        if bold:
            print(f"[white]\[{datetime.now().strftime('%H:%M:%S')}][/white] [bold]{message}[/bold]")
        else:
            print(f"[white]\[{datetime.now().strftime('%H:%M:%S')}][/white] {message}")

    @staticmethod
    def question(message, bold=False, default=None):
        if bold:
            return Prompt.ask(f"[#5F9EA0]\[{datetime.now().strftime('%H:%M:%S')}][/#5F9EA0] [bold]{message}[/bold]", default=default)
        return Prompt.ask(f"[#5F9EA0]\[{datetime.now().strftime('%H:%M:%S')}][/#5F9EA0] {message}", default=default)

    @staticmethod
    def question_with_type(message, choices, bold=False, default=None):
        if bold:
            return Prompt.ask(
                f"[#5F9EA0]\[{datetime.now().strftime('%H:%M:%S')}][/#5F9EA0] [bold]{message}[/bold]", choices=choices, default=default
            )
        return Prompt.ask(f"[#5F9EA0]\[{datetime.now().strftime('%H:%M:%S')}][/#5F9EA0] {message}", choices=choices, default=default)

    @staticmethod
    def confirm(message, bold=False, default=True):
        if bold:
            return Confirm.ask(f"[#5F9EA0]\[{datetime.now().strftime('%H:%M:%S')}][/#5F9EA0] [bold]{message}[/bold]", default=default)
        return Confirm.ask(f"[#5F9EA0]\[{datetime.now().strftime('%H:%M:%S')}][/#5F9EA0] {message}", default=default)
