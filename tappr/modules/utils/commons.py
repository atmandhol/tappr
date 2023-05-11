import typer
import yaml
import base64

from tappr.modules.utils.ui import Picker
from rich import print as rprint
from difflib import Differ


class Commons:
    @staticmethod
    def install_cluster_essentials(ui_helper, state):
        exit_code = ui_helper.sh_call(
            cmd=f"kapp deploy -a kapp-controller -n kube-system -f https://github.com/vmware-tanzu/carvel-kapp-controller/releases/latest/download/release.yml -y",
            msg=":hourglass: Install Kapp Controller",
            spinner_msg="Installing",
            error_msg=":broken_heart: Unable to Install Kapp Controller. Use [bold]--verbose[/bold] flag for error details.",
            state=state,
        )
        if exit_code != 0:
            raise typer.Exit(-1)

        exit_code = ui_helper.sh_call(
            cmd=f"kapp deploy -a secretgen-controller -n kube-system -f https://github.com/vmware-tanzu/carvel-secretgen-controller/releases/latest/download/release.yml -y",
            msg=":hourglass: Install Secretgen Controller",
            spinner_msg="Installing",
            error_msg=":broken_heart: Unable to Install Secretgen Controller. Use [bold]--verbose[/bold] flag for error details.",
            state=state,
        )
        if exit_code != 0:
            raise typer.Exit(-1)
        return

    @staticmethod
    def check_tanzu_cli(ui_helper, state, logger):
        proc, _, _ = ui_helper.progress(cmd=f"tanzu package version", state=state, message="Checking")
        if proc.returncode != 0:
            logger.msg(":broken_heart: tanzu cli checks failed. Use [bold]--verbose[/bold] flag for error details.")
            raise typer.Exit(-1)

    @staticmethod
    def check_and_pick_k8s_context(k8s_context, k8s_helper, logger, ui_helper, state, pick_message=None):
        if k8s_context is None:
            k8s_context = k8s_helper.pick_context(context=state.get("context", None), message=pick_message)
        if k8s_context not in k8s_helper.contexts:
            logger.msg(f":worried: No valid context named [yellow]{k8s_context}[/yellow] found in KUBECONFIG.", bold=False)
            raise typer.Exit(-1)
        if not k8s_context:
            logger.msg(":broken_heart: No valid k8s context found.")
            raise typer.Exit(1)
        Commons.check_tanzu_cli(ui_helper=ui_helper, state=state, logger=logger)
        ui_helper.progress(cmd=f"kubectl config use-context {k8s_context}", message=":hourglass: Setting context", state=state)
        logger.msg(f":file_folder: Using k8s context [yellow]{k8s_context}[/yellow]", bold=False)
        return k8s_context

    @staticmethod
    def list_k8s_context(k8s_helper):
        return k8s_helper.list_context()

    @staticmethod
    def print_smart_diff(old, new):
        for line in Differ().compare(yaml.safe_dump(old).split("\n"), yaml.safe_dump(new).split("\n")):
            if line.startswith("+"):
                rprint(f"[green]{line}[/green]")
            elif line.startswith("-"):
                rprint(f"[red]{line}[/red]")
            elif not line.startswith("   ") and not line.startswith("  -") and not line.startswith("?"):
                print(line)

    @staticmethod
    def get_ns_list(k8s_helper, client):
        ns_list = list()
        success, response = k8s_helper.list_namespaces(client=client)
        if success and hasattr(response, "items"):
            for item in response.items:
                ns_list.append(item.metadata.name)
        return ns_list

    @staticmethod
    def get_custom_object_data(k8s_helper, namespace, name, group, version, plural, client, logger, state):
        success, response = k8s_helper.get_namespaced_custom_objects(
            name=name,
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            client=client,
        )
        if not success:
            logger.msg(f":broken_heart: Cannot find {name} in {plural} in namespace {namespace} on the cluster")
            logger.msg(f"\n{response}", bold=False) if state["verbose"] else None
            raise typer.Exit(1)
        return success, response

    @staticmethod
    def pick_namespace(k8s_helper, client):
        ns_list = Commons.get_ns_list(k8s_helper=k8s_helper, client=client)
        options = ns_list
        if len(options) == 0:
            return None
        if len(options) > 1:
            option, _ = Picker(options, "Pick Namespace to track:").start()
        else:
            return options[0]
        return option

    @staticmethod
    def get_tap_values(k8s_helper, k8s_context, namespace, logger, state):
        success, response = Commons.get_custom_object_data(
            k8s_helper=k8s_helper,
            namespace=namespace,
            name="tap",
            group="packaging.carvel.dev",
            version="v1alpha1",
            plural="packageinstalls",
            client=k8s_helper.custom_clients[k8s_context],
            logger=logger,
            state=state,
        )

        # hack TODO: switch this to use a decent jsonpath lib
        # tap_version_installed = response["spec"]["packageRef"]["versionSelection"]["constraints"]
        tap_values_secret_name = response["spec"]["values"][0]["secretRef"]["name"]

        success, response = k8s_helper.get_namespaced_secret(secret=tap_values_secret_name, namespace=namespace, client=k8s_helper.core_clients[k8s_context])

        if not success:
            logger.msg(f":cry: Unable to get {tap_values_secret_name} from namespace {namespace}")
            raise typer.Exit(-1)
        return success, response

    @staticmethod
    def get_tap_gui_cluster_from_tap_values(tap_values_secret_response, logger):
        try:
            tap_values = yaml.safe_load(base64.b64decode(list(tap_values_secret_response.data.values())[0]).decode())
        except Exception:
            logger.msg(f":cry: TAP Values file secret was not proper yaml")
            raise typer.Exit(1)

        try:
            _ = tap_values["tap_gui"] and tap_values["tap_gui"]["app_config"] and tap_values["tap_gui"]["app_config"]["kubernetes"]
        except KeyError:
            logger.msg(f":cry: tap_gui or app_config not found in TAP values file")
            raise typer.Exit(-1)

        clusters = list()
        for entry in tap_values["tap_gui"]["app_config"]["kubernetes"]["clusterLocatorMethods"][0]["clusters"]:
            clusters.append({"name": entry.get("name"), "url": entry.get("url"), "authProvider": entry.get("authProvider")})
        return clusters
