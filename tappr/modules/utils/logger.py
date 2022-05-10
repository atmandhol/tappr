from rich import print
from rich.prompt import Confirm, Prompt


class TyperLogger:
    @staticmethod
    def debug(message, bold=False):
        if bold:
            print(f"[bold][yellow]{message}[/yellow][/bold]")
        else:
            print(f"[yellow]{message}[/yellow]")

    @staticmethod
    def error(message, bold=False):
        if bold:
            print(f"[bold][red]{message}[/red][/bold]")
        else:
            print(f"[red]{message}[/red]")

    @staticmethod
    def success(message, bold=False):
        if bold:
            print(f"[bold][green]{message}[/green][/bold]")
        else:
            print(f"[green]{message}[/green]")

    @staticmethod
    def msg(message, bold=False):
        if bold:
            print(f"[bold]{message}[/bold]")
        else:
            print(f"{message}")

    @staticmethod
    def important(message, bold=False):
        if bold:
            print(f"[bold]{message}[/bold]")
        else:
            print(f"{message}")

    @staticmethod
    def question(message, bold=False, default=None):
        if bold:
            return Prompt.ask(f"[bold]{message}[/bold]", default=default)
        return Prompt.ask(f"{message}", default=default)

    @staticmethod
    def question_with_type(message, choices, bold=False, default=None):
        if bold:
            return Prompt.ask(
                f"[bold]{message}[/bold]", choices=choices, default=default
            )
        return Prompt.ask(f"{message}", choices=choices, default=default)

    @staticmethod
    def confirm(message, bold=False, default=True):
        if bold:
            return Confirm.ask(f"[bold]{message}[/bold]", default=default)
        return Confirm.ask(f"{message}", default=default)
