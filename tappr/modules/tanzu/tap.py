import os
import hashlib
import typer

from tappr.modules.utils.enums import GITURL, REGISTRY

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


class TanzuApplicationPlatform:
    def __init__(self, subprocess_helper, pivnet_helper, logger, creds_helper, state, ui_helper):
        self.creds_helper = creds_helper
        self.logger = logger
        self.sh = subprocess_helper
        self.pivnet_helpers = pivnet_helper
        self.state = state
        self.ui_helper = ui_helper

    def sh_call(self, cmd, msg, spinner_msg, error_msg):
        return self.ui_helper.sh_call(cmd=cmd, msg=msg, spinner_msg=spinner_msg, error_msg=error_msg, state=self.state)

    def tap_install(self, k8s_context, profile, version, host_os, tap_values_file):
        hash_str = str(k8s_context + profile + version)
        tmp_dir = f"/tmp/{hashlib.md5(hash_str.encode()).hexdigest()}"
        self.logger.msg(f":file_folder: Staging Installation Dir is at [yellow]{tmp_dir}[/yellow]", bold=True)

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

        # tap-install namespace setup
        _, out, _ = self.sh.run_proc(cmd=f"kubectl get ns")
        if "tap-install" not in out.decode():
            exit_code = self.sh_call(
                cmd=f"kubectl create ns tap-install",
                msg=":file_cabinet:  Create TAP install namespace",
                spinner_msg="Creating",
                error_msg=":broken_heart: Unable to create TAP install namespace. Use [bold]--verbose[/bold] flag for error details.",
            )
            if exit_code != 0:
                raise typer.Exit(-1)

        _, out, _ = self.sh.run_proc(cmd=f"kubectl get ns")
        if "tap-install" not in out.decode():
            self.logger.msg(":broken_heart: Unable to find TAP install namespace. Use [bold]--verbose[/bold] flag for error details.")
            raise typer.Exit(-1)

        # Setup registry secret
        cmd = "tanzu secret registry list --namespace tap-install"
        _, out, _ = self.sh.run_proc(cmd=cmd)

        self.sh_call(
            cmd=(
                f"tanzu secret registry update tap-registry --username {install_registry_username} --password {install_registry_password} --server {install_registry_hostname} "
                f"--export-to-all-namespaces --yes --namespace tap-install"
            )
            if "tap-registry" in out.decode()
            else (
                f"tanzu secret registry add tap-registry --username {install_registry_username} --password {install_registry_password} --server {install_registry_hostname} "
                f"--export-to-all-namespaces --yes --namespace tap-install"
            ),
            msg=":key: Setting tanzu registry secret",
            spinner_msg="Setting up",
            error_msg=None,
        )

        # Setup TAP Packages repo
        cmd = "tanzu package repository list --namespace tap-install"
        _, out, _ = self.sh.run_proc(cmd=cmd)

        self.sh_call(
            cmd=f"tanzu package repository update tanzu-tap-repository --url {install_registry_hostname}/tanzu-application-platform/tap-packages:{version} --namespace tap-install"
            if "tanzu-tap-repository" in out.decode()
            else f"tanzu package repository add tanzu-tap-repository --url {install_registry_hostname}/tanzu-application-platform/tap-packages:{version} --namespace tap-install",
            msg=":key: Setting up [yellow]tanzu-tap-repository[/yellow] package repo",
            spinner_msg="Setting up",
            error_msg=None,
        )
        _, out, _ = self.sh.run_proc(cmd=f"tanzu package repository get tanzu-tap-repository --namespace tap-install")
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
        cmd = f"tanzu package install tap -p tap.tanzu.vmware.com -v {version} --values-file {tap_values_file} -n tap-install"
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
