import typer
import json
import os
import yaml
import random
import string

from rich.console import Console
from tappr.modules.changelog.changelog import ChangeLog
from tappr.modules.releasenotes.release_notes import ReleaseNotes
from tappr.modules.test.test_framework import TestFramework
from tappr.modules.tanzu.tap import TanzuApplicationPlatform
from tappr.modules.tanzu.tapgui import TanzuApplicationPlatformGUI
from tappr.modules.utils.commons import Commons
from tappr.modules.utils.helpers import SubProcessHelpers
from tappr.modules.utils.logger import TyperLogger
from tappr.modules.utils.enums import GKE_RELEASE_CHANNELS
from tappr.modules.utils.creds import CredsHelper
from tappr.modules.utils.ui import UI
from tappr.modules.utils.k8s import K8s
from typing import Optional, List

state = {"verbose": False, "context": None}
VERSION = "0.14.0"

typer_logger = TyperLogger()
commons = Commons()
console = Console(color_system="truecolor")
subprocess_helpers = SubProcessHelpers()
creds_helpers = CredsHelper(logger=typer_logger, subprocess_helper=subprocess_helpers)
ui_helpers = UI(subprocess_helper=subprocess_helpers, logger=typer_logger)
test_framework = TestFramework(logger=typer_logger, subprocess_helper=subprocess_helpers, ui_helper=ui_helpers)
k8s_helpers = K8s(state=state, logger=typer_logger)
tap_helpers = TanzuApplicationPlatform(
    subprocess_helper=subprocess_helpers,
    logger=typer_logger,
    creds_helper=creds_helpers,
    state=state,
    ui_helper=ui_helpers,
    k8s_helper=k8s_helpers,
    console=console,
)
tap_gui_helpers = TanzuApplicationPlatformGUI(
    subprocess_helper=subprocess_helpers,
    logger=typer_logger,
    creds_helper=creds_helpers,
    state=state,
    ui_helper=ui_helpers,
    k8s_helper=k8s_helpers,
    console=console,
)

# noinspection PyTypeChecker
app = typer.Typer(help="CLI for Tanzu Application Platform", pretty_exceptions_show_locals=False)

utils_app = typer.Typer(help="Random utils for making life easier.")
cluster_app = typer.Typer(help="Kubernetes cluster CRUD commands")
create_cluster_app = typer.Typer(help="Create Kubernetes clusters.")
delete_cluster_app = typer.Typer(help="Delete Kubernetes clusters.")
registry_app = typer.Typer(help="Manage local docker registry.")
tap_app = typer.Typer(help="Tanzu Application Platform management.")
local_app = typer.Typer(help="Helpers to setup your local environment.")
tap_gui_app = typer.Typer(help="Tanzu Application Platform GUI management.")

cluster_app.add_typer(create_cluster_app, name="create")
cluster_app.add_typer(delete_cluster_app, name="delete")
app.add_typer(cluster_app, name="cluster")
app.add_typer(tap_app, name="tap")
app.add_typer(tap_gui_app, name="gui")
app.add_typer(utils_app, name="utils")
utils_app.add_typer(registry_app, name="registry")
utils_app.add_typer(local_app, name="local")


def local_install(interactive, tool, cmd):
    if interactive:
        ans = typer_logger.confirm(f"Install {tool} ?", default=False)
        if not ans:
            return
    typer_logger.msg(f":package: Installing {tool}", bold=False)
    proc, out, err = ui_helpers.progress(cmd=cmd, state=state, message=f"Downloading and Installing")
    if proc.returncode == 0:
        typer_logger.msg(":rocket: Install [green]complete[/green]")
    else:
        typer_logger.msg(f":broken_heart: Unable to Install [yellow]{tool}[/yellow]. Use [bold]--verbose[/bold] flag for error details.")


# noinspection PyTypedDict
@app.callback()
def tappr(
    verbose: bool = typer.Option(False, help="Logger verbose flag, Set env_var TAPPR_VERBOSE=true to change default to true."),
    context: str = typer.Option(None, help="Kubernetes context to target from the KUBECONFIG, set env_var TAPPR_K8S_CONTEXT to set default"),
):
    if verbose:
        state["verbose"] = True
    elif os.environ.get("TAPPR_VERBOSE", "").lower() == "true":
        state["verbose"] = True
    if context:
        state["context"] = context
    elif os.environ.get("TAPPR_K8S_CONTEXT", None):
        state["context"] = os.environ.get("TAPPR_K8S_CONTEXT")


# noinspection PyTypedDict
@tap_app.callback()
def tap(
    verbose: bool = typer.Option(False, help="Logger verbose flag, Set env_var TAPPR_VERBOSE=true to change default to true."),
    context: str = typer.Option(None, help="Kubernetes context to target from the KUBECONFIG, set env_var TAPPR_K8S_CONTEXT to set default"),
):
    if verbose:
        state["verbose"] = True
    elif os.environ.get("TAPPR_VERBOSE", "").lower() == "true":
        state["verbose"] = True
    if context:
        state["context"] = context
    elif os.environ.get("TAPPR_K8S_CONTEXT", None):
        state["context"] = os.environ.get("TAPPR_K8S_CONTEXT")


@app.command()
def version():
    """
    Show the version of tappr
    """
    # subprocess_helpers.run_pre_req(cmd="pipx list --short | grep tappr", tool="tappr")
    typer_logger.msg(f":white_check_mark: tappr [green]{VERSION}[/green] installed")


@app.command()
def init(
    tanzunet_username: str = typer.Option(None, help="Tanzu Network Username."),
    tanzunet_password: str = typer.Option(None, help="Tanzu Network Password."),
    install_registry_server: str = typer.Option(None, help="Registry where the TAP packages are"),
    registry_server: str = typer.Option(None, help="Default registry server to use while installing tap. e.g. gcr.io, index.docker.io etc."),
    registry_tbs_repo: str = typer.Option(None, help="Default registry repo on the registry server to use for build service. Don't include the registry server or starting /."),
    registry_username: str = typer.Option(None, help="Registry username to use while installing tap"),
    registry_password: str = typer.Option(None, help="Registry password to use while installing tap. If using GCR set this as path to jsonkey file."),
    pkg_relocation_repo: str = typer.Option(None, help="Default registry repo on the registry server to use for relocating TAP packages. Don't include the registry server or starting /."),
):
    """
    Initialize the tappr cli with required configuration.
    """
    creds_helpers.set_config(
        tanzunet_username=tanzunet_username,
        tanzunet_password=tanzunet_password,
        install_registry_server=install_registry_server,
        registry_server=registry_server,
        registry_username=registry_username,
        registry_password=registry_password,
        registry_tbs_repo=registry_tbs_repo,
        pkg_relocation_repo=pkg_relocation_repo,
    )
    typer_logger.msg("\n:runner: [cyan][bold]tappr cluster create --help[/bold][/cyan] to see help for creating k8s clusters.")
    typer_logger.msg(":runner: [cyan][bold]tappr tap install --help[/bold][/cyan] to see help for installing TAP on your k8s clusters.\n")


@utils_app.command()
def changelog(
    log_range: str = typer.Option("all", help="Determine which commits gets included for changelog. The log will be grouped by tags regardless of the range."),
    ignore_dependabot_commits: bool = typer.Option(True, help="Dependabot commits will be ignored from the changelog"),
    ignore_docs_commits: bool = typer.Option(True, help="Docs commits will be ignored from the changelog"),
    output: str = typer.Option("stdout", help="Filename where the changelog output will be stored"),
):
    """
    Generate changelog from git log. You will have an easier time creating changelog if you use conventional commits.

    Examples:

    Generate a changelog for all commits starting from first commit to the tag v0.4.0.

    $ tappr utils changelog --log-range v0.4.0

    Generate a changelog for commits between tag v0.4.1 to the last commit

    $ tappr utils changelog --log-range v0.4.1..HEAD

    Generate a changelog for all commits between tag v0.4.1 and v0.5.0

    $ tappr utils changelog --log-range v0.4.1..v0.5.0

    """

    ChangeLog(logger=typer_logger).generate_changelog(
        log_range=log_range,
        ignore_dependabot_commits=ignore_dependabot_commits,
        ignore_docs_commits=ignore_docs_commits,
        output=output,
    )


@utils_app.command()
def release(
    since_ver: str,
    release_ver: str,
    template_file: str,
    pr_path: str,
    ignore_dependabot_commits: bool = typer.Option(True, help="Dependabot commits will be ignored from the release notes"),
    ignore_docs_commits: bool = typer.Option(True, help="Docs commits will be ignored from the release notes"),
    output: str = typer.Option("stdout", help="Filename where the release notes output will be stored"),
):
    """
    Generate GitHub/Gitlab release notes from git log. You will have an easier time creating release notes if you use conventional commits.

    since_ver: is the previous version. This should be in a valid semver format.

    release_ver: is the version you are trying to release. This should be in a valid semver format.

    template_file: markdown template file to be used for creating releases

    pr_path: is the path to PRs. For e.g. for this repo, its https://github.com/atmandhol/tappr/pull/. This is needed to generate PR links automatically in the release notes

    output: Defaults to stdout. Change to something else for a file output

    """
    ReleaseNotes(logger=typer_logger).generate_releasenotes(
        since_ver=since_ver,
        release_ver=release_ver,
        template_file=template_file,
        pr_path=pr_path,
        ignore_dependabot_commits=ignore_dependabot_commits,
        ignore_docs_commits=ignore_docs_commits,
        output=output,
    )


@utils_app.command()
def test(
    test_file: str,
    output: str = "stdout",
):
    """
    Run pre-defined test on the tappr test framework.

    - test_file: test yaml file that defines the tests to run and context

    output: Defaults to stdout. Change to something else for a file output

    """
    test_framework.run_tests(test_file=test_file, output=output, state=state)


# =============================================================================================
# Local commands
# =============================================================================================
@local_app.command()
def check():
    """
    Run pre-checks for running tappr on the local environment.
    """
    checks_passed = True
    typer_logger.msg("\n:toolbox: Checking core tools that are needed for using [bold][green]tappr[/green][/bold] ...")
    checks_passed = subprocess_helpers.run_pre_req(cmd="docker --version", tool="Docker") and checks_passed
    checks_passed = subprocess_helpers.run_pre_req(cmd="kubectl version --client", tool="kubectl") and checks_passed
    checks_passed = subprocess_helpers.run_pre_req(cmd="tanzu version", tool="tanzu CLI") and checks_passed
    checks_passed = subprocess_helpers.run_pre_req(cmd="ytt --version", tool="ytt") and checks_passed
    checks_passed = subprocess_helpers.run_pre_req(cmd="imgpkg --version", tool="imgpkg") and checks_passed

    if not checks_passed:
        typer_logger.msg("Run [green]tappr utils local setup[/green] to install missing tools.")
        raise typer.Exit(-1)
    typer_logger.success("All checks passed!")

    typer_logger.msg("\n:brick: Checking Infrastructure specific k8s tools that are needed for cluster create/delete commands in [bold][green]tappr[/green][/bold] ...")
    subprocess_helpers.run_pre_req(cmd='gcloud version | grep "Google Cloud SDK"', tool="For [yellow]GKE[/yellow] clusters: gcloud") and checks_passed
    checks_passed = subprocess_helpers.run_pre_req(cmd="kind --version", tool="For [yellow]Kind[/yellow] clusters: Kind") and checks_passed
    checks_passed = subprocess_helpers.run_pre_req(cmd="minikube version", tool="For [yellow]minikube[/yellow] clusters: minikube") and checks_passed
    checks_passed = subprocess_helpers.run_pre_req(cmd="rosa version", tool="For [yellow]RedHat Openshift on AWS[/yellow] clusters: rosa CLI") and checks_passed

    typer_logger.msg("\n:hammer_and_wrench: Checking other tools that are not needed for using [bold][green]tappr[/green][/bold] but nice to have ...")
    subprocess_helpers.run_pre_req(cmd="kapp --version", tool="kapp") and checks_passed
    subprocess_helpers.run_pre_req(cmd="kbld --version", tool="kbld") and checks_passed
    subprocess_helpers.run_pre_req(cmd="kctrl --version", tool="kctrl") and checks_passed
    subprocess_helpers.run_pre_req(cmd="vendir --version", tool="vendir") and checks_passed
    subprocess_helpers.run_pre_req(cmd="ko version", tool="ko") and checks_passed
    subprocess_helpers.run_pre_req(cmd="curl --version", tool="curl") and checks_passed
    subprocess_helpers.run_pre_req(cmd="crane version", tool="crane") and checks_passed
    subprocess_helpers.run_pre_req(cmd="go version", tool="golang") and checks_passed
    subprocess_helpers.run_pre_req(cmd="kp version", tool="kpack CLI") and checks_passed
    subprocess_helpers.run_pre_req(cmd="watch -v", tool="watch") and checks_passed
    subprocess_helpers.run_pre_req(cmd="jq --version", tool="jq") and checks_passed
    subprocess_helpers.run_pre_req(cmd="yq --version", tool="yq") and checks_passed

    typer_logger.msg("\nChecks complete. \n:runner: [cyan][bold]tappr utils local setup[/bold][/cyan] to install missing tools (except tanzu CLI and gcloud SDK).")
    typer_logger.msg(":runner: [cyan][bold]tappr init[/bold][/cyan] to set credentials for using tappr.")
    typer_logger.msg(":runner: [cyan][bold]tappr cluster create --help[/bold][/cyan] to see help for creating k8s clusters.")
    typer_logger.msg(":runner: [cyan][bold]tappr tap install --help[/bold][/cyan] to see help for installing TAP on your k8s clusters.\n")


# noinspection PyBroadException
@local_app.command()
def setup(interactive: bool = True):
    """
    Set up your local with all required tools using brew install.

    """
    _, out, err = subprocess_helpers.run_proc("brew -v")
    if err:
        typer_logger.msg(":mag: brew not found in the system. Installing..")
        _, out, err = subprocess_helpers.run_proc('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
        typer_logger.msg(out, bold=False) if state["verbose"] and out else None
        typer_logger.msg(err, bold=False) if state["verbose"] and out else None
        if err:
            typer_logger.msg(":broken_heart: Unable to install brew. Please manually install brew and try again.")

    local_install(interactive=interactive, tool="docker", cmd="brew install --cask docker")
    local_install(interactive=interactive, tool="kubectl", cmd="brew install kubectl")
    local_install(interactive=interactive, tool="ytt", cmd="brew install ytt")
    local_install(interactive=interactive, tool="imgpkg", cmd="brew install imgpkg")

    local_install(interactive=interactive, tool="kind", cmd="brew install kind")
    local_install(interactive=interactive, tool="minikube", cmd="brew install minikube")
    local_install(interactive=interactive, tool="rosa CLI", cmd="brew install rosa-cli")

    local_install(interactive=interactive, tool="kapp", cmd="brew install kapp")
    local_install(interactive=interactive, tool="kbld", cmd="brew install kbld")
    local_install(interactive=interactive, tool="kctrl", cmd="brew install kctrl")
    local_install(interactive=interactive, tool="vendir", cmd="brew install vendir")
    local_install(interactive=interactive, tool="ko", cmd="brew install ko")
    local_install(interactive=interactive, tool="curl", cmd="brew install curl")
    local_install(interactive=interactive, tool="crane", cmd="brew install crane")
    local_install(interactive=interactive, tool="kpack-cli", cmd="brew tap vmware-tanzu/kpack-cli && brew install kp")

    local_install(interactive=interactive, tool="kubectx", cmd="brew install kubectx")
    local_install(interactive=interactive, tool="fzf", cmd="brew install fzf")
    local_install(interactive=interactive, tool="watch", cmd="brew install watch")
    local_install(interactive=interactive, tool="jq", cmd="brew install jq")
    local_install(interactive=interactive, tool="yq", cmd="brew install yq")


@local_app.command()
def cleanup():
    """
    Cleans up tanzu directories and CLI for a fresh installation.
    """
    cmd = "rm -rf $HOME/tanzu/ && rm /usr/local/bin/tanzu && rm -rf ~/.config/tanzu/ && rm -rf ~/.tanzu/"
    typer_logger.msg(f":broom: Initiating cleanup", bold=False)
    proc, out, err = ui_helpers.progress(cmd=cmd, state=state, message="Cleaning up all tanzu CLI files and configs")
    if proc.returncode == 0:
        typer_logger.msg(":rocket: Cleanup [green]complete[/green]")
    else:
        typer_logger.msg(":broken_heart: Unable to cleanup local. Use [bold]--verbose[/bold] flag for error details.")


# =============================================================================================
# tappr create commands
# =============================================================================================
def check_if_cluster_name_valid(name: str):
    if not name.replace("-", "").isalnum():
        typer_logger.msg(":stop_sign: Invalid cluster name. Should be alphanumeric. Only symbol allowed is (-) hyphen.")
        raise typer.Exit(-1)


@create_cluster_app.command()
def minikube(
    cluster_name,
    cpus: str = typer.Option("max", help="Number of CPUs to allot for cluster"),
    memory: str = typer.Option("max", help="Amount of memory to allot for cluster"),
    driver: str = typer.Option("docker", help="minikube driver to use to create clusters. Other options are virtualbox, parallels, vmwarefusion, hyperkit, vmware, docker"),
    embed_certs: bool = typer.Option(False, help="if true, will embed the certs present at $HOME/.minikube/certs/ in kubeconfig"),
    k8s_version: str = typer.Option("stable", help="Kubernetes version"),
    dns_domain: str = typer.Option("cluster.local", help="The cluster dns domain name used in the Kubernetes cluster"),
):
    """
    Create a minikube cluster.
    """
    exit_code = ui_helpers.sh_call(
        cmd=f"minikube version",
        msg=":magnifying_glass_tilted_left: Checking minikube Installation",
        spinner_msg="Checking",
        error_msg=":broken_heart: is minikube installed?. Use [bold]--verbose[/bold] flag for error details.",
        state=state,
    )
    if exit_code != 0:
        raise typer.Exit(-1)

    check_if_cluster_name_valid(cluster_name)
    cmd = (
        f'minikube start --cpus="{cpus}" --memory="{memory}" --kubernetes-version={k8s_version} --profile={cluster_name} --driver={driver} --embed-certs={embed_certs} --dns-domain={dns_domain}'
    )
    typer_logger.msg(f":package: Creating a minikube cluster with profile named [yellow]{cluster_name}[/yellow].", bold=False)
    proc, out, err = ui_helpers.progress(cmd=cmd, state=state, message="Spinning up a minikube cluster")
    if proc.returncode == 0:
        typer_logger.msg(":rocket: minikube cluster created [green]successfully[/green]")
    else:
        typer_logger.msg(":broken_heart: Unable to create minikube cluster. Use [bold]--verbose[/bold] flag for error details.")

    typer_logger.msg(f"\n:runner: [cyan][bold]minikube tunnel --profile {cluster_name}[/bold][/cyan] in a separate terminal to start a Load Balancer tunnel.")
    typer_logger.msg(":runner: [cyan][bold]tappr tap install {profile} {version}[/bold][/cyan] to install TAP on minikube.")
    typer_logger.msg(f":runner: [cyan][bold]tappr cluster delete minikube {cluster_name}[/bold][/cyan] to delete the cluster.\n")


@create_cluster_app.command()
def kind(cluster_name, customize: bool = typer.Option(False, help="Customize the default config file")):
    """
    Create a multi-node kind cluster.
    """
    exit_code = ui_helpers.sh_call(
        cmd=f"kind --version",
        msg=":magnifying_glass_tilted_left: Checking Kind Installation",
        spinner_msg="Checking",
        error_msg=":broken_heart: is Kind installed?. Use [bold]--verbose[/bold] flag for error details.",
        state=state,
    )
    if exit_code != 0:
        raise typer.Exit(-1)

    check_if_cluster_name_valid(cluster_name)
    kind_config = open(os.path.dirname(os.path.abspath(__file__)) + "/modules/artifacts/clusters/kind.yaml").read()

    if customize:
        kind_config = ui_helpers.yaml_prompt(
            message="KinD Configuration YAML",
            auto_complete_list=[],
            default=kind_config,
        )
        try:
            yaml.safe_load(kind_config)
        except Exception:
            typer_logger.msg(":cry: inline updates were not in valid yaml format. Try again!")
            raise typer.Exit(1)

    cmd = f"cat << EOF | kind create cluster --name {cluster_name} --config -\n{kind_config}\nEOF"
    typer_logger.msg(f":package: Creating a multi-node kind cluster named [yellow]{cluster_name}[/yellow].", bold=False)
    proc, out, err = ui_helpers.progress(cmd=cmd, state=state, message="Spinning up a Kind cluster")
    if proc.returncode == 0:
        typer_logger.msg(":rocket: KinD cluster created [green]successfully[/green]")
    else:
        typer_logger.msg(":broken_heart: Unable to create KinD cluster. Use [bold]--verbose[/bold] flag for error details.")

    typer_logger.msg("\n:runner: [cyan][bold]tappr tap install --help[/bold][/cyan] to see help for installing TAP on your k8s clusters.\n")


def get_latest_gke_version_by_channel(region, channel):
    # Get all supported server configs
    proc, out, _ = ui_helpers.progress(
        cmd=f"gcloud container get-server-config --region={region} --format=json", message=":magnifying_glass_tilted_left: Checking gcloud installation", state=state
    )
    if proc.returncode != 0:
        raise typer.Exit(-1)

    # Get the default project
    server_config = json.loads(out.decode())
    if channel == channel.NONE:
        return server_config["defaultClusterVersion"]

    channels = server_config["channels"]
    for c in channels:
        if c["channel"] == channel:
            return c["defaultVersion"]


@create_cluster_app.command()
def gke(
    cluster_name: str = typer.Option(None, help="Name of the GKE cluster"),
    channel: GKE_RELEASE_CHANNELS = typer.Option(GKE_RELEASE_CHANNELS.STABLE, help="GKE Release Channel"),
    cluster_version: str = typer.Option("auto", help="auto takes the latest in the channel. You can specify a fixed version as well."),
    project: str = typer.Option(None, help="Name of the GCP project. If gcloud is pointing to a specific project, it will be automatically picked up"),
    customize: bool = typer.Option(False, help="Customize the default values"),
    region: str = typer.Option(None, help="GKE cluster region"),
    num_nodes_per_zone: int = typer.Option(None, help="Number of worker nodes in NodePool per zone"),
    new_subnet_name: str = typer.Option(None, help="Provide a name of new subnet to create that will be used for this GKE cluster"),
    new_subnet_range: int = typer.Option(23, help="CIDR range routing prefix bits. Should be between 21-24 for a full TAP install"),
):
    """
    Create a GKE cluster. Assumes gcloud is set to create clusters.
    """
    # Check if gcloud is installed
    proc, out, _ = ui_helpers.progress(cmd=f"gcloud info --format json", message=":magnifying_glass_tilted_left: Checking gcloud installation", state=state)
    if proc.returncode != 0:
        raise typer.Exit(-1)

    # Get the default project
    gcloud_op = json.loads(out.decode())
    gcp_project = gcloud_op["config"]["project"] if not project else project

    # Check if gcloud beta is installed
    # if "beta" not in gcloud_op["installation"]["components"]:
    #     typer_logger.msg(":broken_heart: 'beta' component for gcloud is not installed which is required. Run gcloud components install beta to fix this.")
    #     raise typer.Exit(-1)

    if not cluster_name:
        letters = string.ascii_lowercase
        # This generates a random 10 letter string
        cluster_name = "".join(random.choice(letters) for _ in range(10))

    check_if_cluster_name_valid(cluster_name)

    # Get cluster config defaults. referred to as ccd variable. which is then overridden by cco variable.
    file_path = os.path.dirname(os.path.abspath(__file__)) + "/modules/artifacts/clusters/gke_defaults.json"
    try:
        ccd = json.loads(open(file_path, "r").read())
    except Exception:
        typer_logger.msg(":broken_heart: Unable to read artifacts/clusters/gke_defaults.json")
        raise typer.Exit(-1)

    auto_complete_list = [
        "region",
        "machine_type",
        "image_type",
        "disk_type",
        "disk_size",
        "max_pods_per_node",
        "num_nodes",
        "network",
        "sub_network",
    ]

    tanzunet_username = None
    # noinspection PyBroadException
    try:
        tanzunet_username = creds_helpers.get("tanzunet_username", "INSTALL_REGISTRY_USERNAME").split("@")[0]
        tanzunet_username = "".join(ch for ch in tanzunet_username if ch.isalnum())
    except Exception:
        pass

    cco = dict()
    if customize:
        data = ui_helpers.yaml_prompt(
            message="GKE Configuration JSON",
            auto_complete_list=auto_complete_list,
            default=json.dumps(ccd, indent=2, sort_keys=True),
        )
        # Cluster config overrides
        try:
            cco = json.loads(data)
        except Exception:
            typer_logger.msg(":broken_heart: Customized output was not a proper json")
            raise typer.Exit(-1)
    if not region:
        region = ccd.get("region") if "region" not in cco else cco.get("region")
    if not num_nodes_per_zone:
        num_nodes_per_zone = ccd.get("num_nodes") if "num_nodes" not in cco else cco.get("num_nodes")
    if cluster_version == "auto":
        cluster_version = get_latest_gke_version_by_channel(region=region, channel=channel)
    if channel != GKE_RELEASE_CHANNELS.NONE:
        channel = channel.lower()
    # subprocess_helpers.run_proc("gcloud components install beta -q")
    cmd = (
        f'gcloud container --project "{gcp_project}" clusters create "{cluster_name}" --region "{region}" '
        f'--no-enable-basic-auth --cluster-version "{cluster_version}" '
        f'--release-channel "{channel}" '
        f"--machine-type \"{ccd.get('machine_type') if 'machine_type' not in cco else cco.get('machine_type')}\" "
        f"--image-type \"{ccd.get('image_type') if 'image_type' not in cco else cco.get('image_type')}\" "
        f"--disk-type \"{ccd.get('disk_type') if 'disk_type' not in cco else cco.get('disk_type')}\" "
        f"--disk-size \"{ccd.get('disk_size') if 'disk_size' not in cco else cco.get('disk_size')}\" --metadata disable-legacy-endpoints=true "
        f'--scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring",'
        f'"https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" '
        f"--max-pods-per-node \"{ccd.get('max_pods_per_node') if 'max_pods_per_node' not in cco else cco.get('max_pods_per_node')}\" "
        f'--num-nodes "{num_nodes_per_zone}" '
        f"--logging=SYSTEM,WORKLOAD --monitoring=SYSTEM --enable-ip-alias "
        f"--network \"{ccd.get('network') if 'network' not in cco else cco.get('network')}\" "
        f"--no-enable-intra-node-visibility --default-max-pods-per-node \"{ccd.get('max_pods_per_node') if 'max_pods_per_node' not in cco else cco.get('max_pods_per_node')}\" "
        f"--no-enable-master-authorized-networks --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver"
        f"{' --no-enable-autoupgrade' if channel not in ['rapid', 'regular', 'stable'] else ''} --no-enable-managed-prometheus --no-enable-autorepair "
        f"--max-surge-upgrade 1 --max-unavailable-upgrade 0 --enable-shielded-nodes "
        f"--workload-pool={gcp_project}.svc.id.goog --labels=used_by={tanzunet_username if tanzunet_username else 'tappr'},created_by=tappr"
    )
    if not new_subnet_name:
        cmd += f" --subnetwork \"{ccd.get('sub_network') if 'sub_network' not in cco else cco.get('sub_network')}\" "
    else:
        cmd += f" --create-subnetwork name={new_subnet_name},range=/{new_subnet_range} "

    cmd = cmd.replace("{project}", gcp_project).replace("{region}", region)
    typer_logger.msg(f":package: Creating a GKE cluster named [yellow]{cluster_name}[/yellow] in project [yellow]{gcp_project}[/yellow]", bold=False)
    proc, out, err = ui_helpers.progress(cmd=cmd, state=state, message="Spinning up a GKE cluster")
    if proc.returncode == 0:
        typer_logger.msg(":rocket: GKE Cluster created [green]successfully[/green]")
    else:
        typer_logger.msg(":broken_heart: Unable to create GKE cluster. Use [bold]--verbose[/bold] flag for error details.")
        raise typer.Exit(-1)

    typer_logger.msg("\n:runner: [cyan][bold]tappr tap install --help[/bold][/cyan] to see help for installing TAP on your k8s clusters.\n")


# =============================================================================================
# tappr delete commands
# =============================================================================================
@delete_cluster_app.command()
def kind(cluster_name):
    """
    Delete a kind cluster.
    """
    cmd = f"kind delete cluster --name {cluster_name}"
    typer_logger.msg(f":package: Deleting kind cluster named [yellow]{cluster_name}[/yellow].", bold=False)
    proc, out, err = ui_helpers.progress(cmd=cmd, state=state, message="Deleting Kind cluster")
    if proc.returncode == 0:
        typer_logger.msg(":rocket: KinD cluster deleted [green]successfully[/green]")
    else:
        typer_logger.msg(":broken_heart: Unable to delete KinD cluster. Use [bold]--verbose[/bold] flag for error details.")
        raise typer.Exit(-1)


@delete_cluster_app.command()
def minikube(cluster_name):
    """
    Delete a minikube cluster.
    """
    cmd = f"minikube delete --profile {cluster_name}"
    typer_logger.msg(f":package: Deleting minikube cluster named [yellow]{cluster_name}[/yellow].", bold=False)
    proc, out, err = ui_helpers.progress(cmd=cmd, state=state, message="Deleting minikube cluster")
    if proc.returncode == 0:
        typer_logger.msg(":rocket: minikube cluster deleted [green]successfully[/green]")
    else:
        typer_logger.msg(":broken_heart: Unable to delete minikube cluster. Use [bold]--verbose[/bold] flag for error details.")
        raise typer.Exit(-1)


@delete_cluster_app.command()
def gke(cluster_name, region: str = "us-east4"):
    """
    Delete a GKE cluster.
    """
    cmd = f"gcloud container clusters delete {cluster_name} --region {region} -q"
    typer_logger.msg(f":bomb: Deleting GKE cluster named [yellow]{cluster_name}[/yellow]", bold=False)
    proc, out, err = ui_helpers.progress(cmd=cmd, state=state, message="Deleting a GKE cluster")
    if proc.returncode == 0:
        typer_logger.msg(":rocket: GKE Cluster deleted [green]successfully[/green]")
    else:
        typer_logger.msg(":broken_heart: Unable to delete GKE cluster. Use [bold]--verbose[/bold] flag for error details.")
        raise typer.Exit(-1)


# =============================================================================================
# Local Registry commands
# =============================================================================================
@registry_app.command()
def start():
    # Start Docker registry
    cmd = f"docker run -d -p 5001:5000 --restart=always --name local-registry registry:2"

    typer_logger.msg(f":whale: Starting Local Docker registry on port [yellow]5001[/yellow].", bold=False)
    proc, out, err = ui_helpers.progress(cmd=cmd, state=state, message="Starting container")
    if proc.returncode == 125:
        typer_logger.msg(":rocket: Local Docker registry already [green]running[/green]")
    elif proc.returncode == 0:
        typer_logger.msg(":rocket: Local Docker registry [green]started[/green]")
    else:
        typer_logger.msg(":broken_heart: Unable to create KinD cluster. Use [bold]--verbose[/bold] flag for error details.")

    # Connect registry to kind cluster network
    cmd = f"docker network connect kind local-registry"
    typer_logger.msg(f":whale: Connecting registry with [yellow]kind[/yellow] network.", bold=False)
    proc, out, err = ui_helpers.progress(cmd=cmd, state=state, message="Connecting")
    if proc.returncode == 1:
        typer_logger.msg(":rocket: Local docker registry already [green]part of kind network[/green]")
    elif proc.returncode == 0:
        typer_logger.msg(":rocket: Local docker registry [green]now part of kind network[/green]")
    else:
        typer_logger.msg(":broken_heart: Unable to add local registry to kind network. Use [bold]--verbose[/bold] flag for error details.")


@registry_app.command()
def stop():
    cmd = f"docker container stop local-registry && docker container rm -v local-registry"
    typer_logger.msg(f":whale: Stopping Local Docker registry on port [yellow]5001[/yellow].", bold=False)
    proc, out, err = ui_helpers.progress(cmd=cmd, state=state, message="Stopping container")
    if proc.returncode == 1:
        typer_logger.msg(":rocket: Local Docker registry [red]not running[/red]")
    elif proc.returncode == 0:
        typer_logger.msg(":rocket: Local Docker registry [green]stopped[/green]")
    else:
        typer_logger.msg(":broken_heart: Unable to stop and delete local registry. Use [bold]--verbose[/bold] flag for error details.")


# =============================================================================================
# TAP commands
# =============================================================================================
@tap_app.command()
def install_cluster_essentials():
    """
    Install only Cluster Essentials.

    """
    commons.install_cluster_essentials(ui_helper=ui_helpers, state=state)
    typer_logger.msg("\n:runner: [cyan][bold]tappr tap install --help[/bold][/cyan] to see help for installing TAP on your k8s clusters.\n")


# noinspection PyShadowingNames
@tap_app.command()
def install(
    profile: str = typer.Argument("full", help="TAP profile. Values can be full, iterate, build, run or view"),
    version: str = typer.Argument("1.4.0", help="Version of TAP. it should be of format x.x.x or x.x.x-build.x"),
    namespace: str = typer.Option("tap-install", help="Namespace where TAP should be installed"),
    ingress_domain: str = typer.Option("127.0.0.1.nip.io", help="Shared Ingress Domain"),
    ingress_issuer: str = typer.Option("", help='Shared Ingress Issuer. Can also use "tap-ingress-selfsigned" to use the OOTB self signed cert'),
    k8s_distribution: str = typer.Option("", help="Use openshift if installing on Openshift cluster, else use default"),
    tbs_repo_push_secret: str = typer.Option("tbs-repo-push", help="Name of the push secret that needs to be created"),
    tbs_tanzunet_pull_secret: str = typer.Option("tbs-tanzunet-pull", help="Name of the pull secret for Tanzu Network that needs to be created for TBS"),
    tanzunet_pull_secret: str = typer.Option("tanzunet-pull", help="Name of the pull secret for Tanzu Network that needs to be created for TAP install"),
    repo_pull_secret: str = typer.Option("repo-pull", help="Name of the push secret that needs to be created"),
    supply_chain: str = typer.Option("basic", help='OOTB Supply chain to install. Other values are "testing" and "testing_scanning"'),
    contour_infra: str = typer.Option("vsphere", help="Supported values are aws, azure and vsphere"),
    service_type: str = typer.Option("LoadBalancer", help="Accepted values are LoadBalancer, NodePort and ClusterIP"),
    ca_cert_file: str = typer.Option(None, help="Absolute URL to the file that contains CA Cert data that should be added to shared TAP configuration"),
    skip_cluster_essentials: bool = typer.Option(False, help="Skip Cluster Essentials installation as its already installed or the user is using TKG or some flavor that already has it."),
    exclude_package: Optional[List[str]] = typer.Option(None),
    tap_values_file: str = None,
    wait: bool = typer.Option(False, help="Wait for the TAP install to complete"),
):
    """
    Install TAP. Make sure to run tappr init before installing TAP.

    """
    if profile not in ["full", "iterate", "run", "build", "view"]:
        raise ValueError("Invalid profile. Values can be full, iterate, build, run or view.")
    tap_helpers.tap_install(
        profile=profile,
        version=version,
        tap_values_file=tap_values_file,
        wait=wait,
        namespace=namespace,
        skip_cluster_essentials=skip_cluster_essentials,
        ingress_domain=ingress_domain,
        ingress_issuer=ingress_issuer,
        k8s_distribution=k8s_distribution,
        tbs_repo_push_secret=tbs_repo_push_secret,
        tbs_tanzunet_pull_secret=tbs_tanzunet_pull_secret,
        tanzunet_pull_secret=tanzunet_pull_secret,
        repo_pull_secret=repo_pull_secret,
        supply_chain=supply_chain,
        ca_cert_file=ca_cert_file,
        contour_infra=contour_infra,
        service_type=service_type,
        exclude_package=exclude_package,
    )
    typer_logger.msg("\n:runner: [cyan][bold]tappr tap status[/bold][/cyan] to see the status of your TAP install.")
    typer_logger.msg(":runner: [cyan][bold]tappr tap edit --show[/bold][/cyan] to edit TAP values config on the cluster.")
    typer_logger.msg(":runner: [cyan][bold]tappr tap setup[/bold][/cyan] to setup developer namespace.")
    typer_logger.msg(":runner: [cyan][bold]tappr tap upgrade {new-version}[/bold][/cyan] to upgrade TAP version.\n")


@tap_app.command()
def setup(
    namespace: str = typer.Option("default", help="Developer namespace to setup"),
):
    """
    Setup Developer Namespace.

    """
    tap_helpers.developer_ns_setup(namespace=namespace)


@tap_app.command()
def edit(
    namespace: str = typer.Option("tap-install", help="TAP installation namespace"),
    from_file: str = typer.Option(
        None,
        help="Yaml file path containing tap values to shallow merge (first level only) with the existing tap values on the cluster. " "Inline editor is not invoked if this option is used.",
    ),
    force: bool = typer.Option(False, help="Force save the changes to the yaml file without any user prompt"),
    show: bool = typer.Option(True, help="Show the current content of the tap values file on the cluster in the inline editor. Defaults to false for security purposes."),
):
    """
    Modify TAP Installation.

    """
    tap_helpers.edit_tap_values(namespace=namespace, from_file=from_file, force=force, show_current=show)


@tap_app.command()
def ingress_ip(service: str = "envoy", namespace: str = typer.Option("tanzu-system-ingress", help="Tanzu System Ingress installation namespace")):
    """
    Get the Tanzu System Ingress External IP of the TAP cluster.

    """
    tap_helpers.ingress_ip(service=service, namespace=namespace)


# noinspection PyShadowingNames
@tap_app.command()
def relocate(
    version: str = typer.Option(None, help="Select the version of TAP you want to relocate from Tanzu Network to your Registry"),
    tanzunet_username: str = typer.Option(None, help="Tanzu Network Username, defaults to config set by tappr init."),
    tanzunet_password: str = typer.Option(None, help="Tanzu Network Password, defaults to config set by tappr init."),
    registry_server: str = typer.Option(None, help="Default registry server to use while installing tap, defaults to config set by tappr init. e.g. gcr.io, index.docker.io etc."),
    registry_username: str = typer.Option(None, help="Registry username to use while installing tap, defaults to config set by tappr init"),
    registry_password: str = typer.Option(None, help="Registry password to use while installing tap, defaults to config set by tappr init"),
    pkg_relocation_repo: str = typer.Option(None, help="Default registry repo on the registry server to use for relocating TAP packages, defaults to config set by tappr init."),
    wait: bool = typer.Option(True, help="Wait for the relocation to finish or run it in a separate thread in the background."),
):
    """
    Relocate packages from Tanzu Network to your Registry

    """
    tap_helpers.relocate(
        version=version,
        tanzunet_username=tanzunet_username,
        tanzunet_password=tanzunet_password,
        registry_server=registry_server,
        registry_username=registry_username,
        registry_password=registry_password,
        pkg_relocation_repo=pkg_relocation_repo,
        wait=wait,
    )


# noinspection PyShadowingNames
@tap_app.command()
def upgrade(
    version: str,
    namespace: str = typer.Option("tap-install", help="TAP installation namespace"),
    wait: bool = typer.Option(False, help="Wait for the TAP install to complete"),
):
    """
    Upgrade TAP to a higher version.

    """
    tap_helpers.upgrade(version=version, wait=wait, namespace=namespace)


@tap_app.command()
def uninstall(package: str = typer.Option("tap", help="Package name to uninstall"), namespace: str = "tap-install"):
    """
    Uninstall TAP.

    """
    tap_helpers.uninstall(package=package, namespace=namespace)


@tap_app.command()
def status(namespace: str = typer.Option("tap-install", help="TAP installation namespace")):
    """
    Get TAP installation status.

    """
    tap_helpers.status(namespace=namespace)


@tap_gui_app.command()
def server_ip(service: str = "server", namespace: str = "tap-gui"):
    """
    Get the TAP GUI server external IP.

    """
    tap_gui_helpers.server_ip(service=service, namespace=namespace)


# noinspection PyShadowingBuiltins
@tap_gui_app.command()
def list(namespace: str = typer.Option("tap-install", help="TAP installation namespace on the cluster where TAP GUI is located")):
    """
    Get a list of Clusters tracked by TAP GUI.

    """
    tap_gui_helpers.list_clusters(namespace=namespace)


@tap_gui_app.command()
def track(
    namespace: str = typer.Option("tap-install", help="TAP installation namespace on the cluster where TAP GUI is located"),
    tap_viewer_sa: str = typer.Option("tap-gui-viewer", help="TAP Viewer service account in the cluster and namespace to be tracked"),
):
    """
    Add cluster credential to TAP GUI for tracking resources on GUI.

    """
    tap_gui_helpers.track_cluster(tap_install_namespace=namespace, tap_viewer_service_account=tap_viewer_sa)


@tap_gui_app.command()
def untrack(namespace: str = typer.Option("tap-install", help="TAP installation namespace on the cluster where TAP GUI is located")):
    """
    Remove cluster credential from TAP GUI.

    """
    tap_gui_helpers.untrack_cluster(tap_install_namespace=namespace)


if __name__ == "__main__":
    app()
