import typer
import yaml

from rich import print as rprint
from difflib import Differ


class Commons:
    @staticmethod
    def check_tanzu_cli(ui_helper, state):
        exit_code = ui_helper.sh_call(
            cmd=f"tanzu package version",
            msg=":magnifying_glass_tilted_left: Checking tanzu CLI",
            spinner_msg="Checking",
            error_msg=":broken_heart: tanzu cli checks failed. Use [bold]--verbose[/bold] flag for error details.",
            state=state,
        )
        if exit_code != 0:
            raise typer.Exit(-1)

    @staticmethod
    def check_and_pick_k8s_context(k8s_context, k8s_helper, logger, ui_helper, state):
        if k8s_context is None:
            k8s_context = k8s_helper.pick_context(context=state.get("context", None))
        if k8s_context not in k8s_helper.contexts:
            logger.msg(f":worried: No valid context named [yellow]{k8s_context}[/yellow] found in KUBECONFIG.", bold=False)
            raise typer.Exit(-1)
        if not k8s_context:
            logger.msg(":broken_heart: No valid k8s context found.")
            raise typer.Exit(1)
        Commons.check_tanzu_cli(ui_helper=ui_helper, state=state)
        ui_helper.progress(cmd=f"kubectl config use-context {k8s_context}", message=":hourglass: Setting context", state=state)
        logger.msg(f":file_folder: Using k8s context [yellow]{k8s_context}[/yellow]", bold=False)
        return k8s_context

    @staticmethod
    def print_smart_diff(old, new):
        for line in Differ().compare(yaml.safe_dump(old).split("\n"), yaml.safe_dump(new).split("\n")):
            if line.startswith("+"):
                rprint(f"[green]{line}[/green]")
            elif line.startswith("-"):
                rprint(f"[red]{line}[/red]")
            elif not line.startswith("   ") and not line.startswith("  -"):
                print(line)

    @staticmethod
    def get_ns_list(k8s_helper, client):
        ns_list = list()
        success, response = k8s_helper.list_namespaces(client=client)
        if success and hasattr(response, "items"):
            for item in response.items:
                ns_list.append(item.metadata.name)
        return ns_list
