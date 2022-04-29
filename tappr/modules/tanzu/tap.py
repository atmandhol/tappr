import os
import hashlib
import typer
import base64
import yaml
from rich import print as rprint
from difflib import Differ

import tappr.modules.utils.k8s
from tappr.modules.utils.enums import GITURL, REGISTRY

auto_complete_list = [
    "profile",
    "ceip_policy_disclosed",
    "buildservice",
    "kp_default_repository",
    "kp_default_repository_username",
    "kp_default_repository_password",
    "tanzunet_username",
    "tanzunet_password",
    "descriptor_name",
    "supply_chain",
    "cnrs",
    "domain_name",
    "ootb_supply_chain_basic",
    "registry",
    "server",
    "repository",
    "gitops",
    "ssh_secret",
    "learningcenter",
    "ingressDomain",
    "tap_gui",
    "service_type",
    "ingressEnabled",
    "ingressDomain",
    "app_config",
    "app",
    "baseUrl",
    "catalog",
    "locations",
    "type",
    "target",
    "backend",
    "cors",
    "origin",
    "metadata_store",
    "grype",
    "namespace",
    "targetImagePullSecret",
    "ca_cert_data",
    "certificates",
    "duration",
    "renewBefore",
    "configFileContents",
    "logLevel",
    "contour",
    "replicas",
    "useProxyProtocol",
    "hostPorts",
    "enable",
    "service",
    "annotations",
    "externalTrafficPolicy",
    "LBType",
    "nodePorts",
    "terminationGracePeriodSeconds",
    "infrastructure_provider",
    "hostNetwork",
    "ingress",
    "external",
    "internal",
    "reuse_crds",
    "local_dns",
    "domain",
    "pdb",
    "provider",
    "ingressSecret",
    "ingressClass",
    "service_account",
    "git_implementation",
    "registry",
    "repository",
    "gitops",
    "username",
    "branch",
    "commit_message",
    "email",
    "repository_prefix",
    "ssh_secret",
    "cluster_builder",
    "user_name",
    "user_email",
    "excluded_templates",
    "authSecret",
    "name",
    "allow_unmatched_images",
    "custom_ca_secrets",
    "custom_cas",
    "deployment_namespace",
    "limits_cpu",
    "limits_memory",
    "quota",
    "pod_number",
    "replicas",
    "requests_cpu",
    "requests_memory",
    "app_service_type",
    "auth_proxy_host",
    "db_host",
    "db_replicas",
    "db_sslmode",
    "pg_limit_memory",
    "app_req_cpu",
    "app_limit_memory",
    "app_req_memory",
    "auth_proxy_port",
    "db_name",
    "db_port",
    "api_port",
    "app_limit_cpu",
    "app_replicas",
    "pg_req_memory",
    "priority_class_name",
    "use_cert_manager",
    "api_host",
    "db_password",
    "storage_class_name",
    "database_request_storage",
    "add_default_rw_service_account",
    "enable_automatic_dependency_updates",
]

pivnet_products = {
    "darwin": {
        "CLI_BUNDLE": "1178279",
        "CLUSTER_ESSENTIALS_BUNDLE": "1105820",
        "CLUSTER_ESSENTIALS_BUNDLE_SHA": "registry.tanzu.vmware.com/tanzu-cluster-essentials/cluster-essentials-bundle@sha256:82dfaf70656b54dcba0d4def85ccae1578ff27054e7533d08320244af7fb0343",
    },
    "linux": {
        "CLI_BUNDLE": "1178280",
        "CLUSTER_ESSENTIALS_BUNDLE": "1105818",
        "CLUSTER_ESSENTIALS_BUNDLE_SHA": "registry.tanzu.vmware.com/tanzu-cluster-essentials/cluster-essentials-bundle@sha256:82dfaf70656b54dcba0d4def85ccae1578ff27054e7533d08320244af7fb0343",
    },
}


# noinspection PyBroadException
class TanzuApplicationPlatform:
    def __init__(self, subprocess_helper, pivnet_helper, logger, creds_helper, state, ui_helper, k8s_helper):
        self.creds_helper = creds_helper
        self.logger = logger
        self.sh = subprocess_helper
        self.pivnet_helpers = pivnet_helper
        self.state = state
        self.ui_helper = ui_helper
        self.k8s_helper: tappr.modules.utils.k8s.K8s = k8s_helper

    def sh_call(self, cmd, msg, spinner_msg, error_msg):
        return self.ui_helper.sh_call(cmd=cmd, msg=msg, spinner_msg=spinner_msg, error_msg=error_msg, state=self.state)

    def tap_install(self, profile, version, host_os, k8s_context, tap_values_file, namespace: str = "tap-install"):
        if k8s_context is None:
            k8s_context = self.k8s_helper.pick_context()

        if k8s_context not in self.k8s_helper.contexts:
            self.logger.msg(f":woman_police_officer: No valid context named [yellow]{k8s_context}[/yellow] found in KUBECONFIG.", bold=False)
            raise typer.Exit(-1)

        exit_code = self.sh_call(
            cmd=f"kubectl cluster-info",
            msg=":man_police_officer: Checking k8s cluster and kubectl",
            spinner_msg="Checking",
            error_msg=":broken_heart: Unable to connect to k8s cluster. Use [bold]--verbose[/bold] flag for error details.",
        )
        if exit_code != 0:
            raise typer.Exit(-1)

        check_tanzu_cli(ui_helper=self.ui_helper, state=self.state)

        self.ui_helper.progress(cmd=f"kubectl config use-context {k8s_context}", message=":man_police_officer: Setting context", state=self.state)
        self.logger.msg(f":file_folder: Using k8s context [yellow]{k8s_context}[/yellow] for installation", bold=False)

        hash_str = str(profile + version)
        tmp_dir = f"/tmp/{hashlib.md5(hash_str.encode()).hexdigest()}"
        self.logger.msg(f":file_folder: Staging Installation Dir is at [yellow]{tmp_dir}[/yellow]", bold=False)

        if not os.path.isdir(tmp_dir):
            self.sh_call(
                cmd=f"mkdir -p {tmp_dir}",
                msg=":file_folder: Creating Staging Dir",
                spinner_msg="Creating dir",
                error_msg=":broken_heart: Unable to create staging directory. Use [bold]--verbose[/bold] flag for error details.",
            )

        install_registry_hostname = self.creds_helper.get("default_tap_install_registry", "INSTALL_REGISTRY_HOSTNAME")
        install_registry_username = self.creds_helper.get("tanzunet_username", "INSTALL_REGISTRY_USERNAME")
        install_registry_password = self.creds_helper.get("tanzunet_password", "INSTALL_REGISTRY_PASSWORD")
        registry_server = self.creds_helper.get("default_registry_server", "REGISTRY_SERVER")
        registry_repo = self.creds_helper.get("default_registry_repo", "REGISTRY_REPO")
        registry_username = self.creds_helper.get("default_registry_username", "REGISTRY_USERNAME")
        registry_password = self.creds_helper.get("default_registry_password", "REGISTRY_PASSWORD")
        pivnet_uaa_token = self.creds_helper.get("pivnet_uaa_token", "PIVNET_TOKEN")

        if os.path.isfile(registry_password):
            registry_password = open(registry_password, "r").read()

        os.environ["TAP_VERSION"] = version
        os.environ["INSTALL_BUNDLE"] = pivnet_products[host_os]["CLUSTER_ESSENTIALS_BUNDLE_SHA"]

        # Cluster essentials
        exit_code = self.pivnet_helpers.login(api_token=pivnet_uaa_token, state=self.state)
        if exit_code != 0:
            raise typer.Exit(-1)

        cluster_essential_tar = f"{tmp_dir}/tanzu-cluster-essentials-{host_os}-amd64-1.0.0.tgz"
        if not os.path.isfile(cluster_essential_tar):
            exit_code = self.pivnet_helpers.download(
                product_slug="tanzu-cluster-essentials",
                release_version="1.0.0",
                product_file_id=pivnet_products[host_os]["CLUSTER_ESSENTIALS_BUNDLE"],
                download_dir=tmp_dir,
                state=self.state,
            )
            if exit_code != 0:
                raise typer.Exit(-1)

        if not os.path.isfile(f"{tmp_dir}/install.sh"):
            exit_code = self.sh_call(
                cmd=f"tar xvf {cluster_essential_tar} -C {tmp_dir}",
                msg=":compression:  Extracting Cluster essentials",
                spinner_msg="Extracting",
                error_msg=":broken_heart: Unable to extract cluster essentials. Use [bold]--verbose[/bold] flag for error details.",
            )
            if exit_code != 0:
                raise typer.Exit(-1)

        os.chdir(tmp_dir)
        exit_code = self.sh_call(
            cmd=f"bash {tmp_dir}/install.sh",
            msg=":man_mechanic_medium-light_skin_tone: Install Cluster Essentials",
            spinner_msg="Installing",
            error_msg=":broken_heart: Unable to Install cluster essentials. Use [bold]--verbose[/bold] flag for error details.",
        )
        if exit_code != 0:
            raise typer.Exit(-1)

        _, out, _ = self.sh.run_proc(cmd=f"kubectl get ns")
        if namespace not in out.decode():
            exit_code = self.sh_call(
                cmd=f"kubectl create ns {namespace}",
                msg=":file_cabinet:  Create TAP install namespace",
                spinner_msg="Creating",
                error_msg=":broken_heart: Unable to create TAP install namespace. Use [bold]--verbose[/bold] flag for error details.",
            )
            if exit_code != 0:
                raise typer.Exit(-1)

        _, out, _ = self.sh.run_proc(cmd=f"kubectl get ns")
        if namespace not in out.decode():
            self.logger.msg(":broken_heart: Unable to find TAP install namespace. Use [bold]--verbose[/bold] flag for error details.")
            raise typer.Exit(-1)

        # Setup registry secret
        cmd = f"tanzu secret registry list --namespace {namespace}"
        _, out, _ = self.sh.run_proc(cmd=cmd)

        self.sh_call(
            cmd=(
                f"tanzu secret registry update tap-registry --username {install_registry_username} --password {install_registry_password} --server {install_registry_hostname} "
                f"--export-to-all-namespaces --yes --namespace {namespace}"
            )
            if "tap-registry" in out.decode()
            else (
                f"tanzu secret registry add tap-registry --username {install_registry_username} --password {install_registry_password} --server {install_registry_hostname} "
                f"--export-to-all-namespaces --yes --namespace {namespace}"
            ),
            msg=":key: Setting tanzu registry secret",
            spinner_msg="Setting up",
            error_msg=None,
        )

        # Setup TAP Packages repo
        cmd = f"tanzu package repository list --namespace {namespace}"
        _, out, _ = self.sh.run_proc(cmd=cmd)

        self.sh_call(
            cmd=f"tanzu package repository update tanzu-tap-repository --url {install_registry_hostname}/tanzu-application-platform/tap-packages:{version} --namespace {namespace}"
            if "tanzu-tap-repository" in out.decode()
            else f"tanzu package repository add tanzu-tap-repository --url {install_registry_hostname}/tanzu-application-platform/tap-packages:{version} --namespace {namespace}",
            msg=":key: Setting up [yellow]tanzu-tap-repository[/yellow] package repo",
            spinner_msg="Setting up",
            error_msg=None,
        )
        _, out, _ = self.sh.run_proc(cmd=f"tanzu package repository get tanzu-tap-repository --namespace {namespace}")
        self.logger.msg(out.decode(), bold=False) if self.state["verbose"] and out else None

        if not tap_values_file:
            tap_values_yml = open(os.path.dirname(os.path.abspath(__file__)).replace("/tanzu", f"/artifacts/profiles/{profile}.yml"), "r").read()
            tap_values_yml = tap_values_yml.replace("$INSTALL_REGISTRY_HOSTNAME", install_registry_hostname)
            tap_values_yml = tap_values_yml.replace("$INSTALL_REGISTRY_USERNAME", install_registry_username)
            tap_values_yml = tap_values_yml.replace("$INSTALL_REGISTRY_PASSWORD", install_registry_password)
            tap_values_yml = tap_values_yml.replace("$REGISTRY_SERVER", registry_server)
            tap_values_yml = tap_values_yml.replace("$REGISTRY_REPO", registry_repo)
            tap_values_yml = tap_values_yml.replace("$REGISTRY_USERNAME", registry_username)
            tap_values_yml = tap_values_yml.replace("$REGISTRY_PASSWORD", registry_password)
            tap_values_file = f"{tmp_dir}/tap-values.yml"
            self.logger.msg(f":memo: Creating values yml file at [yellow]{tap_values_file}[/yellow]")
            open(f"{tap_values_file}", "w").write(tap_values_yml)

        # TAP install
        cmd = f"tanzu package install tap -p tap.tanzu.vmware.com -v {version} --values-file {tap_values_file} -n {namespace}"
        self.logger.debug(f"Running {cmd}. Can take up to 15-20 minutes depending on your machine.") if self.state["verbose"] and out else None
        self.sh_call(
            cmd=cmd,
            msg=":wine_glass: Installing [yellow]TAP[/yellow]",
            spinner_msg="Waiting to reconcile",
            error_msg=None,
        )
        self.logger.msg(":rocket: TAP is installed. Use tappr tap setup to setup developer namespace.")

        return

    def developer_ns_setup(self, namespace):
        _, out, _ = self.sh.run_proc(cmd=f"kubectl get ns")
        if namespace not in out.decode():
            exit_code = self.sh_call(
                cmd=f"kubectl create ns {namespace}",
                msg=f":file_cabinet:  Creating [yellow]{namespace}[/yellow] as it does not exist.",
                spinner_msg="Creating",
                error_msg=f":broken_heart: Unable to create namespace [yellow]{namespace}[/yellow]. Use [bold]--verbose[/bold] flag for error details.",
            )
            if exit_code != 0:
                raise typer.Exit(-1)

        private_git = self.logger.confirm(f":cd: Are you going to use private git repos ?", default=False)

        dev_yaml_path = os.path.dirname(os.path.abspath(__file__)).replace("/modules/tanzu", "") + f"/modules/artifacts/profiles/developer.yml"
        if not private_git:
            exit_code = self.sh_call(
                cmd=f"kubectl create secret generic git-ssh -n {namespace}",
                msg=":key: Create generic SSH secret",
                spinner_msg="Creating",
                error_msg=":broken_heart: Unable to create SSH secret. Use [bold]--verbose[/bold] flag for error details.",
            )
            if exit_code != 0:
                raise typer.Exit(-1)
        else:
            ssh_secret_name = self.logger.question(f":key: Git SSH secret name in TAP values (Set git-ssh if you don't know) ?")
            git_url = self.logger.question_with_type(
                message=f":page_with_curl: Git Host URL ?",
                choices=[GITURL.GITLAB_VMWARE_SSH, GITURL.GIT_SSH, GITURL.OTHER],
            )
            if git_url == GITURL.OTHER:
                git_url = self.logger.question(":octopus: Enter your git url")
            ssh_key_loc = self.logger.question(":key: Enter path to your SSH private key (PEM)")

            exit_code = self.sh_call(
                cmd=f"kp secret create {ssh_secret_name} --git-url {git_url} --git-ssh-key {ssh_key_loc} -n {namespace}",
                msg=":man_gesturing_ok: Create Git secret on the cluster",
                spinner_msg="Creating",
                error_msg=":broken_heart: Unable to create SSH secret. Use [bold]--verbose[/bold] flag for error details.",
            )
            if exit_code != 0:
                raise typer.Exit(-1)

        registry_server = self.creds_helper.get("default_registry_server", "REGISTRY_SERVER")
        registry_password = self.creds_helper.get("default_registry_password", "REGISTRY_PASSWORD")
        reg = self.logger.question_with_type(
            message=f":framed_picture:  Image Registry ?",
            choices=[REGISTRY.GCR, REGISTRY.DOCKERHUB, REGISTRY.OTHER],
            default=REGISTRY.GCR if "gcr.io" in registry_server else None,
        )

        if reg == REGISTRY.GCR:
            reg_key = self.logger.question(
                f":key: Where is your GCR service account .json key file ?", default=registry_password if "gcr.io" in registry_server else None
            )
            cmd = f"kp secret create registry-credentials --gcr {reg_key} -n {namespace}"
        elif reg == REGISTRY.DOCKERHUB:
            docker_id = self.logger.question(f":whale: Where is your dockerhub-id ?")
            cmd = f"kp secret create registry-credentials --dockerhub {docker_id} -n {namespace}"
        else:
            registry = self.logger.question(f":key: Registry url ?")
            registry_user = self.logger.question(f":key: Registry UserId ?")
            cmd = f"kp secret create registry-credentials --registry {registry} --registry-user {registry_user} -n {namespace}"

        exit_code = self.sh_call(
            cmd=cmd,
            msg=":man_gesturing_ok: Create Registry secret on the cluster",
            spinner_msg="Creating",
            error_msg=":broken_heart: Unable to create Registry secret. Use [bold]--verbose[/bold] flag for error details.",
        )
        if exit_code != 0:
            raise typer.Exit(-1)

        exit_code = self.sh_call(
            cmd=f"kubectl -n {namespace} apply -f {dev_yaml_path}",
            msg=f":man_gesturing_ok: Setting up developer namespace {namespace}",
            spinner_msg="Finalizing",
            error_msg=":broken_heart: Unable to setup developer namespace. Use [bold]--verbose[/bold] flag for error details.",
        )
        if exit_code != 0:
            raise typer.Exit(-1)

        exit_code = self.sh_call(
            cmd=f"kubectl config set-context --current --namespace={namespace}",
            msg=f":man_gesturing_ok: Setting namespace {namespace} as default in current context",
            spinner_msg="Finalizing",
            error_msg=":broken_heart: Unable to set namespace as default. Use [bold]--verbose[/bold] flag for error details.",
        )
        if exit_code != 0:
            raise typer.Exit(-1)

    def ingress_ip(self, k8s_context: str, service: str, namespace: str):
        if k8s_context is None:
            k8s_context = self.k8s_helper.pick_context()
        if k8s_context not in self.k8s_helper.contexts:
            self.logger.msg(f":woman_police_officer: No valid context named [yellow]{k8s_context}[/yellow] found in KUBECONFIG.", bold=False)
            raise typer.Exit(-1)
        if not k8s_context:
            self.logger.msg(":broken_heart: No valid k8s context found.")
            raise typer.Exit(1)
        success, response = self.k8s_helper.get_namespaced_service(
            service=service, namespace=namespace, client=self.k8s_helper.core_clients[k8s_context]
        )
        if success:
            for ingress in response.status.load_balancer.ingress:
                print(ingress.ip)
        else:
            self.logger.msg(":broken_heart: No external Ingress IP found")
            self.logger.msg(f"\n{response}", bold=False) if self.state["verbose"] else None

    def edit_tap_values(self, k8s_context: str, namespace: str, from_file: str, force: bool, show_current: bool):
        if k8s_context is None:
            k8s_context = self.k8s_helper.pick_context()
        if k8s_context not in self.k8s_helper.contexts:
            self.logger.msg(f":woman_police_officer: No valid context named [yellow]{k8s_context}[/yellow] found in KUBECONFIG.", bold=False)
            raise typer.Exit(-1)
        if not k8s_context:
            self.logger.msg(":broken_heart: No valid k8s context found.")
            raise typer.Exit(1)

        success, response = self.k8s_helper.get_namespaced_custom_objects(
            name="tap",
            group="packaging.carvel.dev",
            version="v1alpha1",
            namespace="tap-install",
            plural="packageinstalls",
            client=self.k8s_helper.custom_clients[k8s_context],
        )
        if not success:
            self.logger.msg(":broken_heart: Cannot find tap package on the cluster. is it installed?")
            self.logger.msg(f"\n{response}", bold=False) if self.state["verbose"] else None
            raise typer.Exit(1)

        # hack TODO: switch this to use a decent jsonpath lib
        # tap_version_installed = response["spec"]["packageRef"]["versionSelection"]["constraints"]
        tap_values_secret_name = response["spec"]["values"][0]["secretRef"]["name"]

        success, response = self.k8s_helper.get_namespaced_secret(
            secret=tap_values_secret_name, namespace=namespace, client=self.k8s_helper.core_clients[k8s_context]
        )

        if success:
            new_cluster_tap_values = str()
            try:
                og_cluster_tap_values = yaml.safe_load(base64.b64decode(list(response.data.values())[0]).decode())
            except Exception:
                self.logger.msg(":cry: tap-install-values secret was not proper yaml")
                raise typer.Exit(1)

            if from_file:
                # Get the yaml data from the file
                if os.path.isfile(from_file):
                    try:
                        yaml_updates = yaml.safe_load(open(from_file, "r").read())
                    except Exception:
                        self.logger.msg(":cry: provided file was not valid yaml")
                        raise typer.Exit(1)
                    new_cluster_tap_values = {**og_cluster_tap_values, **yaml_updates}
            else:
                if show_current:
                    default = yaml.safe_dump(og_cluster_tap_values)
                else:
                    default = ""
                data = self.ui_helper.yaml_prompt(
                    message="Enter tap-values.yaml file updates. Press [ESC] and then [ENTER] when you are done\n",
                    auto_complete_list=auto_complete_list,
                    default=default,
                )
                try:
                    yaml_updates = yaml.safe_load(data)
                except Exception:
                    self.logger.msg(":cry: inline updates were not in valid yaml format. Try again!")
                    raise typer.Exit(1)
                if show_current:
                    new_cluster_tap_values = yaml_updates
                else:
                    if yaml_updates:
                        new_cluster_tap_values = {**og_cluster_tap_values, **yaml_updates}
                    else:
                        new_cluster_tap_values = og_cluster_tap_values

            self.logger.msg(":notebook: Input recorded. Calculating diff with current file")
            print_smart_diff(og_cluster_tap_values, new_cluster_tap_values)

            if not force:
                save_it = self.logger.confirm(":question_mark: Do you want to make this edit?")
                if not save_it:
                    self.logger.msg(":sweat_smile: Not making any updates. Maybe some other time.")
                    raise typer.Exit(0)

            # hack: TODO: if the data object structure changes, it will have to be adjusted here. currently I assume there is only 1 key
            data_key = list(response.data.keys())[0]
            body = {"data": {data_key: base64.b64encode(yaml.safe_dump(new_cluster_tap_values).encode()).decode()}}
            success, response = self.k8s_helper.patch_namespaced_secret(
                client=self.k8s_helper.core_clients[k8s_context], secret=tap_values_secret_name, namespace=namespace, body=body
            )
            if not success:
                self.logger.msg(":broken_heart: Unable to edit the configuration secret on TAP cluster. Try again later.")
                self.logger.msg(f"\n{response}", bold=False) if self.state["verbose"] else None
                raise typer.Exit(-1)

        else:
            self.logger.msg(f":broken_heart: {tap_values_secret_name} secret not found in the k8s cluster. is TAP installed properly?")
            self.logger.msg(f"\n{response}", bold=False) if self.state["verbose"] else None

    def upgrade(self, version: str, k8s_context: str, namespace: str = "tap-install"):
        if k8s_context is None:
            k8s_context = self.k8s_helper.pick_context()
        if k8s_context not in self.k8s_helper.contexts:
            self.logger.msg(f":woman_police_officer: No valid context named [yellow]{k8s_context}[/yellow] found in KUBECONFIG.", bold=False)
            raise typer.Exit(-1)
        if not k8s_context:
            self.logger.msg(":broken_heart: No valid k8s context found.")
            raise typer.Exit(1)
        check_tanzu_cli(ui_helper=self.ui_helper, state=self.state)
        self.ui_helper.progress(cmd=f"kubectl config use-context {k8s_context}", message=":man_police_officer: Setting context", state=self.state)
        self.logger.msg(f":file_folder: Using k8s context [yellow]{k8s_context}[/yellow] for installation", bold=False)

        install_registry_hostname = self.creds_helper.get("default_tap_install_registry", "INSTALL_REGISTRY_HOSTNAME")

        cmd = f"tanzu package installed list --namespace {namespace}"
        _, out, _ = self.sh.run_proc(cmd=cmd)
        if "tap.tanzu.vmware.com" not in out.decode():
            self.logger.msg(":broken_heart: TAP package not found. Nothing to upgrade. Please check if TAP is installed")
            raise typer.Exit(1)

        self.sh_call(
            cmd=f"tanzu package repository update tanzu-tap-repository --url {install_registry_hostname}/tanzu-application-platform/tap-packages:{version} --namespace {namespace}",
            msg=":key: Setting up [yellow]tanzu-tap-repository[/yellow] package repo",
            spinner_msg="Setting up",
            error_msg=None,
        )
        _, out, _ = self.sh.run_proc(cmd=f"tanzu package repository get tanzu-tap-repository --namespace {namespace}")
        self.logger.msg(out.decode(), bold=False) if self.state["verbose"] and out else None

        self.sh_call(
            cmd=f"tanzu package installed update tap -p tap.tanzu.vmware.com -v {version} -n {namespace}",
            msg=f":wine_glass: Updating [yellow]TAP[/yellow] to version [yellow]{version}[/yellow]",
            spinner_msg="Updating. Waiting to reconcile..",
            error_msg=None,
        )
        self.logger.msg(":rocket: TAP is upgraded")


def check_tanzu_cli(ui_helper, state):
    exit_code = ui_helper.sh_call(
        cmd=f"tanzu package version",
        msg=":man_police_officer: Checking tanzu CLI",
        spinner_msg="Checking",
        error_msg=":broken_heart: tanzu cli checks failed. Use [bold]--verbose[/bold] flag for error details.",
        state=state,
    )
    if exit_code != 0:
        raise typer.Exit(-1)


def print_smart_diff(old, new):
    for line in Differ().compare(yaml.safe_dump(old).split("\n"), yaml.safe_dump(new).split("\n")):
        if line.startswith("+"):
            rprint(f"[green]{line}[/green]")
        elif line.startswith("-"):
            rprint(f"[red]{line}[/red]")
        elif not line.startswith("   ") and not line.startswith("  -"):
            print(line)
