import base64
import hashlib
import json
import os
import time

import typer
import yaml
from rich import print as rprint

import tappr.modules.utils.k8s
from tappr.modules.utils.commons import Commons

commons = Commons()

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


# noinspection PyBroadException
class TanzuApplicationPlatform:
    def __init__(self, subprocess_helper, pivnet_helper, logger, creds_helper, state, ui_helper, k8s_helper, console):
        self.console = console
        self.creds_helper = creds_helper
        self.install_registry_server = self.creds_helper.get("install_registry_server", "INSTALL_REGISTRY_SERVER")
        self.pivnet_products = {
            "darwin": {
                "CLI_BUNDLE": "1246418",
                "CLUSTER_ESSENTIALS_BUNDLE": "1263761",
                "CLUSTER_ESSENTIALS_BUNDLE_SHA": f"{self.install_registry_server}/tanzu-cluster-essentials/cluster-essentials-bundle@sha256:e00f33b92d418f49b1af79f42cb13d6765f1c8c731f4528dfff8343af042dc3e",
                "VERSION": "1.2.0",
            },
            "linux": {
                "CLI_BUNDLE": "1246421",
                "CLUSTER_ESSENTIALS_BUNDLE": "1263760",
                "CLUSTER_ESSENTIALS_BUNDLE_SHA": f"{self.install_registry_server}/tanzu-cluster-essentials/cluster-essentials-bundle@sha256:e00f33b92d418f49b1af79f42cb13d6765f1c8c731f4528dfff8343af042dc3e",
                "VERSION": "1.2.0",
            },
        }
        self.logger = logger
        self.sh = subprocess_helper
        self.pivnet_helpers = pivnet_helper
        self.state = state
        self.ui_helper = ui_helper
        self.k8s_helper: tappr.modules.utils.k8s.K8s = k8s_helper

    def sh_call(self, cmd, msg, spinner_msg, error_msg):
        return self.ui_helper.sh_call(cmd=cmd, msg=msg, spinner_msg=spinner_msg, error_msg=error_msg, state=self.state)

    def tap_install(self, profile, version, host_os, tap_values_file, wait: bool, namespace: str = "tap-install"):
        k8s_context = commons.check_and_pick_k8s_context(k8s_context=None, k8s_helper=self.k8s_helper, logger=self.logger, ui_helper=self.ui_helper, state=self.state)
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

        tanzunet_username = self.creds_helper.get("tanzunet_username", "INSTALL_REGISTRY_USERNAME")
        tanzunet_password = self.creds_helper.get("tanzunet_password", "INSTALL_REGISTRY_PASSWORD")
        pivnet_uaa_token = self.creds_helper.get("pivnet_uaa_token", "PIVNET_TOKEN")

        registry_server = self.creds_helper.get("registry_server", "REGISTRY_SERVER")
        registry_username = self.creds_helper.get("registry_username", "REGISTRY_USERNAME")
        registry_password = self.creds_helper.get("registry_password", "REGISTRY_PASSWORD")

        # This is where TAP packages get relocated
        # registry_tap_package_repo = self.creds_helper.get("registry_tap_package_repo", "REGISTRY_TAP_PACKAGE_REPO")
        # This is your TAP install and Build service repo info
        registry_tbs_repo = self.creds_helper.get("registry_tbs_repo", "REGISTRY_TBS_REPO")

        if os.path.isfile(registry_password):
            registry_password = open(registry_password, "r").read()

        os.environ["TAP_VERSION"] = version
        os.environ["INSTALL_BUNDLE"] = self.pivnet_products[host_os]["CLUSTER_ESSENTIALS_BUNDLE_SHA"]
        os.environ["INSTALL_REGISTRY_HOSTNAME"] = self.install_registry_server
        os.environ["INSTALL_REGISTRY_USERNAME"] = tanzunet_username
        os.environ["INSTALL_REGISTRY_PASSWORD"] = tanzunet_password

        # Cluster essentials
        exit_code = self.pivnet_helpers.login(api_token=pivnet_uaa_token, state=self.state)
        if exit_code != 0:
            raise typer.Exit(-1)

        cluster_essential_tar = f"{tmp_dir}/tanzu-cluster-essentials-{host_os}-amd64-{self.pivnet_products[host_os]['VERSION']}.tgz"
        if not os.path.isfile(cluster_essential_tar):
            exit_code = self.pivnet_helpers.download(
                product_slug="tanzu-cluster-essentials",
                release_version=self.pivnet_products[host_os]["VERSION"],
                product_file_id=self.pivnet_products[host_os]["CLUSTER_ESSENTIALS_BUNDLE"],
                download_dir=tmp_dir,
                state=self.state,
            )
            if exit_code != 0:
                raise typer.Exit(-1)

        if not os.path.isfile(f"{tmp_dir}/cluster-essentials/install.sh"):
            exit_code = self.sh_call(
                cmd=f"mkdir -p {tmp_dir}/cluster-essentials && tar xvf {cluster_essential_tar} -C {tmp_dir}/cluster-essentials",
                msg=":compression:  Extracting Cluster essentials",
                spinner_msg="Extracting",
                error_msg=":broken_heart: Unable to extract cluster essentials. Use [bold]--verbose[/bold] flag for error details.",
            )
            if exit_code != 0:
                raise typer.Exit(-1)

        os.chdir(tmp_dir + "/cluster-essentials")
        exit_code = self.sh_call(
            cmd=f"bash {tmp_dir}/cluster-essentials/install.sh --yes",
            msg=":hourglass: Install Cluster Essentials",
            spinner_msg="Installing",
            error_msg=":broken_heart: Unable to Install cluster essentials. Use [bold]--verbose[/bold] flag for error details.",
        )
        if exit_code != 0:
            raise typer.Exit(-1)

        ns_list = commons.get_ns_list(k8s_helper=self.k8s_helper, client=self.k8s_helper.core_clients[k8s_context])
        if namespace not in ns_list:
            success, response = self.k8s_helper.create_namespace(namespace=namespace, client=self.k8s_helper.core_clients[k8s_context])
            if not success:
                self.logger.msg(f"Error response {response}") if self.state["verbose"] else None
                self.logger.msg(":broken_heart: Unable to create TAP install namespace. Use [bold]--verbose[/bold] flag for error details.")
                raise typer.Exit(-1)

        ns_list = commons.get_ns_list(k8s_helper=self.k8s_helper, client=self.k8s_helper.core_clients[k8s_context])
        if namespace not in ns_list:
            self.logger.msg(":broken_heart: Unable to find TAP install namespace. Use [bold]--verbose[/bold] flag for error details.")
            raise typer.Exit(-1)

        # Setup registry secret
        cmd = f"tanzu secret registry list --namespace {namespace}"
        _, out, _ = self.sh.run_proc(cmd=cmd)

        self.sh_call(
            cmd=(
                f"tanzu secret registry update tanzunet-registry-creds --username '{tanzunet_username}' --password '{tanzunet_password}' --server {self.install_registry_server} "
                f"--export-to-all-namespaces --yes --namespace {namespace}"
            )
            if "tanzunet-registry-creds" in out.decode()
            else (
                f"tanzu secret registry add tanzunet-registry-creds --username '{tanzunet_username}' --password '{tanzunet_password}' --server {self.install_registry_server} "
                f"--export-to-all-namespaces --yes --namespace {namespace}"
            ),
            msg=":key: Setting up TAP Install Registry secret",
            spinner_msg="Setting up",
            error_msg=None,
        )

        self.sh_call(
            cmd=(
                f"tanzu secret registry update tanzunet-registry-creds-tbs --username '{tanzunet_username}' --password '{tanzunet_password}' --server {self.install_registry_server} "
                f"--export-to-all-namespaces --yes --namespace {namespace}"
            )
            if "tanzunet-registry-creds-tbs" in out.decode()
            else (
                f"tanzu secret registry add tanzunet-registry-creds-tbs --username '{tanzunet_username}' --password '{tanzunet_password}' --server {self.install_registry_server} "
                f"--export-to-all-namespaces --yes --namespace {namespace}"
            ),
            msg=":key: Setting up TAP Install Registry secret for TBS",
            spinner_msg="Setting up",
            error_msg=None,
        )

        self.sh_call(
            cmd=(
                f"tanzu secret registry update registry-credentials-tbs --username '{registry_username}' --password '{registry_password}' --server {registry_server} "
                f"--export-to-all-namespaces --yes --namespace {namespace}"
            )
            if "registry-credentials-tbs" in out.decode()
            else (
                f"tanzu secret registry add registry-credentials-tbs --username '{registry_username}' --password '{registry_password}' --server {registry_server} "
                f"--export-to-all-namespaces --yes --namespace {namespace}"
            ),
            msg=":key: Setting up User Registry secret",
            spinner_msg="Setting up",
            error_msg=None,
        )

        self.sh_call(
            cmd=(
                f"tanzu secret registry update registry-credentials --username '{registry_username}' --password '{registry_password}' --server {registry_server} "
                f"--export-to-all-namespaces --yes --namespace {namespace}"
            )
            if "registry-credentials" in out.decode()
            else (
                f"tanzu secret registry add registry-credentials --username '{registry_username}' --password '{registry_password}' --server {registry_server} "
                f"--export-to-all-namespaces --yes --namespace {namespace}"
            ),
            msg=":key: Setting up User Registry secret for TBS",
            spinner_msg="Setting up",
            error_msg=None,
        )

        # Setup TAP Packages repo
        cmd = f"tanzu package repository list --namespace {namespace}"
        _, out, _ = self.sh.run_proc(cmd=cmd)

        self.sh_call(
            cmd=f"tanzu package repository update tanzu-tap-repository --url {self.install_registry_server}/tanzu-application-platform/tap-packages:{version} --namespace {namespace}"
            if "tanzu-tap-repository" in out.decode()
            else f"tanzu package repository add tanzu-tap-repository --url {self.install_registry_server}/tanzu-application-platform/tap-packages:{version} --namespace {namespace}",
            msg=":key: Setting up [yellow]tanzu-tap-repository[/yellow] package repo",
            spinner_msg="Setting up",
            error_msg=None,
        )
        _, out, _ = self.sh.run_proc(cmd=f"tanzu package repository get tanzu-tap-repository --namespace {namespace}")
        self.logger.msg(out.decode(), bold=False) if self.state["verbose"] and out else None

        if not tap_values_file:
            tap_values_yml = open(os.path.dirname(os.path.abspath(__file__)).replace("/tanzu", f"/artifacts/profiles/{profile}.yml"), "r").read()
            tap_values_yml = tap_values_yml.replace("$INSTALL_REGISTRY_USERNAME", tanzunet_username)
            tap_values_yml = tap_values_yml.replace("$INSTALL_REGISTRY_PASSWORD", tanzunet_password)
            tap_values_yml = tap_values_yml.replace("$REGISTRY_SERVER", registry_server)
            tap_values_yml = tap_values_yml.replace("$REGISTRY_USERNAME", registry_username)
            tap_values_yml = tap_values_yml.replace("$REGISTRY_PASSWORD", registry_password)
            tap_values_yml = tap_values_yml.replace("$REGISTRY_TBS_REPO", registry_tbs_repo)
            tap_values_yml = tap_values_yml.replace("$INSTALL_NS", namespace)
            tap_values_file = f"{tmp_dir}/tap-values.yml"
            self.logger.msg(f":memo: Creating values yml file at [yellow]{tap_values_file}[/yellow]")
            open(f"{tap_values_file}", "w").write(tap_values_yml)

        # TAP install
        cmd = f"tanzu package install tap -p tap.tanzu.vmware.com -v {version} --values-file {tap_values_file} -n {namespace} --wait={'false' if not wait else 'true'}"
        self.logger.debug(f"Running {cmd}. Can take up to 15-20 minutes depending on your machine.") if self.state["verbose"] and out else None
        self.sh_call(
            cmd=cmd,
            msg=":wine_glass: Installing [yellow]TAP[/yellow]",
            spinner_msg="Waiting to reconcile",
            error_msg=None,
        )
        if wait:
            self.logger.msg(":rocket: TAP is installed. Use tappr tap setup to setup developer namespace.")
        else:
            self.logger.msg(":rocket: TAP install started on the cluster. Use tappr tap setup to setup developer namespace.")

        return

    def developer_ns_setup(self, namespace, install_ns="tap-install"):
        k8s_context = commons.check_and_pick_k8s_context(k8s_context=None, k8s_helper=self.k8s_helper, logger=self.logger, ui_helper=self.ui_helper, state=self.state)
        ns_list = commons.get_ns_list(k8s_helper=self.k8s_helper, client=self.k8s_helper.core_clients[k8s_context])
        if namespace not in ns_list:
            self.logger.msg(f":construction: Creating [yellow]{namespace}[/yellow] as it does not exist.")
            success, response = self.k8s_helper.create_namespace(namespace=namespace, client=self.k8s_helper.core_clients[k8s_context])
            if not success:
                self.logger.msg(f"Error response {response}") if self.state["verbose"] else None
                self.logger.msg(":broken_heart: Unable to create namespace [yellow]{namespace}[/yellow]. Use [bold]--verbose[/bold] flag for error details.")
                raise typer.Exit(-1)
            ns_list = commons.get_ns_list(k8s_helper=self.k8s_helper, client=self.k8s_helper.core_clients[k8s_context])
            if namespace not in ns_list:
                self.logger.msg(f":broken_heart: Unable to create namespace {namespace}. Use [bold]--verbose[/bold] flag for error details.")
                raise typer.Exit(-1)

        dev_yaml_path = os.path.dirname(os.path.abspath(__file__)).replace("/modules/tanzu", "") + f"/modules/artifacts/rbac/developer.yml"
        hash_str = str(time.time())
        tmp_dir = f"/tmp/{hashlib.md5(hash_str.encode()).hexdigest()}"
        open(tmp_dir, "w").write(open(dev_yaml_path, "r").read().replace("{$$namespace}", namespace))

        exit_code = self.sh_call(
            cmd=f"kubectl -n {namespace} apply -f {tmp_dir}",
            msg=f":sunglasses: Setting up developer namespace {namespace}",
            spinner_msg="Finalizing",
            error_msg=":broken_heart: Unable to setup developer namespace. Use [bold]--verbose[/bold] flag for error details.",
        )
        if exit_code != 0:
            raise typer.Exit(-1)

        exit_code = self.sh_call(
            cmd=f"kubectl config set-context --current --namespace={namespace}",
            msg=f":sunglasses: Setting namespace {namespace} as default in current context",
            spinner_msg="Finalizing",
            error_msg=":broken_heart: Unable to set namespace as default. Use [bold]--verbose[/bold] flag for error details.",
        )
        if exit_code != 0:
            raise typer.Exit(-1)

        if_add_test_template = self.logger.confirm(":test_tube: Do you want to add a test pipeline?", default=False)
        if if_add_test_template:
            # {$$testTaskImage}
            test_image = self.logger.question(":test_tube: What base image do you want to use for test task? (e.g. gradle, golang, python etc.)", default="gradle")
            # {$$testTaskCmd}
            test_cmd = self.logger.question(":test_tube: Enter test command for running your tests (e.g. [cyan]./mvnw test[/cyan], [cyan]go test -v ./...[/cyan] etc.)", default="./mvnw test")

            template_base_path = os.path.dirname(os.path.abspath(__file__)).replace("/modules/tanzu", "") + f"/modules/artifacts/templates/test-pipeline.yml"
            hash_str = str(time.time())
            tmp_dir = f"/tmp/{hashlib.md5(hash_str.encode()).hexdigest()}"
            open(tmp_dir, "w").write(open(template_base_path, "r").read().replace("{$$testTaskImage}", test_image).replace("{$$testTaskCmd}", test_cmd))
            exit_code = self.sh_call(
                cmd=f"kubectl -n {namespace} apply -f {tmp_dir}",
                msg=f":sunglasses: Setting up test pipeline in namespace {namespace}",
                spinner_msg="Finalizing",
                error_msg=":broken_heart: Unable to add tekton test pipeline to namespace. Use [bold]--verbose[/bold] flag for error details.",
            )
            if exit_code != 0:
                raise typer.Exit(-1)

        if_add_scan_template = self.logger.confirm(":magnifying_glass_tilted_left: Do you want to add a scan policy?", default=False)
        if if_add_scan_template:
            # {$$notAllowedSeverities}
            not_allowed_levels = self.logger.question(
                ':magnifying_glass_tilted_left: What vuln levels are not allowed? (Comma separated list e.g. [cyan]["Critical", "High"][/cyan] etc.)', default="[]"
            )
            try:
                json.loads(not_allowed_levels)
            except Exception:
                self.logger.msg(f":broken_heart: Unable to parse the input. Make sure it's a comma separated list.")
                raise typer.Exit(-1)

            template_base_path = os.path.dirname(os.path.abspath(__file__)).replace("/modules/tanzu", "") + f"/modules/artifacts/templates/scan-policy.yml"
            hash_str = str(time.time())
            tmp_dir = f"/tmp/{hashlib.md5(hash_str.encode()).hexdigest()}"
            open(tmp_dir, "w").write(open(template_base_path, "r").read().replace("{$$notAllowedSeverities}", f" notAllowedSeverities := {not_allowed_levels}"))
            exit_code = self.sh_call(
                cmd=f"kubectl -n {namespace} apply -f {tmp_dir}",
                msg=f":sunglasses: Setting up scan policy in namespace {namespace}",
                spinner_msg="Finalizing",
                error_msg=":broken_heart: Unable to add scan policy to namespace. Use [bold]--verbose[/bold] flag for error details.",
            )
            if exit_code != 0:
                raise typer.Exit(-1)

            # Check if grype is installed
            k8s_context = commons.check_and_pick_k8s_context(k8s_context=None, k8s_helper=self.k8s_helper, logger=self.logger, ui_helper=self.ui_helper, state=self.state)
            success, response = self.k8s_helper.list_namespaced_custom_objects(
                group="packaging.carvel.dev",
                version="v1alpha1",
                namespace=install_ns,
                plural="packageinstalls",
                client=self.k8s_helper.custom_clients[k8s_context],
            )
            for item in response["items"]:
                if "status" in item:
                    if item["status"]["conditions"][0]["type"] == "ReconcileSucceeded" and item["metadata"]["name"] == "grype":
                        grype_version = item["status"]["version"]
                        self.logger.debug(f":package: Grype {grype_version} package detected. Installing grype in namespace {namespace}")

                        hash_str = str(time.time())
                        tmp_dir = f"/tmp/{hashlib.md5(hash_str.encode()).hexdigest()}"
                        # TODO: replace registry-credentials with the secret that was in the values file for grype.
                        # TODO: This might not work for people using custom tap-values.yaml file.
                        open(tmp_dir, "w").write(f"namespace: {namespace}\ntargetImagePullSecret: registry-credentials")
                        exit_code = self.sh_call(
                            cmd=f"tanzu package install grype-scanner-{namespace} --package-name grype.scanning.apps.tanzu.vmware.com --version {grype_version} --namespace {install_ns} --values-file {tmp_dir} ",
                            msg=f":sunglasses: Installing grype scanner in namespace {namespace}",
                            spinner_msg="Finalizing",
                            error_msg=":broken_heart: Unable to install grype scanner. Use [bold]--verbose[/bold] flag for error details.",
                        )
                        if exit_code != 0:
                            raise typer.Exit(-1)

    def ingress_ip(self, service: str, namespace: str):
        k8s_context = commons.check_and_pick_k8s_context(k8s_context=None, k8s_helper=self.k8s_helper, logger=self.logger, ui_helper=self.ui_helper, state=self.state)
        success, response = self.k8s_helper.get_namespaced_service(service=service, namespace=namespace, client=self.k8s_helper.core_clients[k8s_context])
        if success:
            try:
                # This fails when you try to get a public ip when contour is not installed as load balancer,
                # or you are trying to do this in a build cluster
                for ingress in response.status.load_balancer.ingress:
                    print(ingress.ip)
            except Exception:
                self.logger.msg(":broken_heart: No external Ingress IP found")
        else:
            self.logger.msg(":broken_heart: No external Ingress IP found")
            self.logger.msg(f"\n{response}", bold=False) if self.state["verbose"] else None

    def edit_tap_values(self, namespace: str, from_file: str, force: bool, show_current: bool):
        k8s_context = commons.check_and_pick_k8s_context(k8s_context=None, k8s_helper=self.k8s_helper, logger=self.logger, ui_helper=self.ui_helper, state=self.state)

        success, response = commons.get_custom_object_data(
            k8s_helper=self.k8s_helper,
            namespace=namespace,
            name="tap",
            group="packaging.carvel.dev",
            version="v1alpha1",
            plural="packageinstalls",
            client=self.k8s_helper.custom_clients[k8s_context],
            logger=self.logger,
            state=self.state,
        )

        # hack TODO: switch this to use a decent jsonpath lib
        # tap_version_installed = response["spec"]["packageRef"]["versionSelection"]["constraints"]
        tap_values_secret_name = response["spec"]["values"][0]["secretRef"]["name"]

        success, response = self.k8s_helper.get_namespaced_secret(secret=tap_values_secret_name, namespace=namespace, client=self.k8s_helper.core_clients[k8s_context])

        if success:
            new_cluster_tap_values = str()
            try:
                og_cluster_tap_values = yaml.safe_load(base64.b64decode(list(response.data.values())[0]).decode())
            except Exception:
                self.logger.msg(f":cry: {tap_values_secret_name} secret was not proper yaml")
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
                    message="Update TAP Values YAML File",
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
            commons.print_smart_diff(og_cluster_tap_values, new_cluster_tap_values)

            if not force:
                save_it = self.logger.confirm(":question_mark: Do you want to make this edit?")
                if not save_it:
                    self.logger.msg(":sweat_smile: Not making any updates. Maybe some other time.")
                    raise typer.Exit(0)

            # hack: TODO: if the data object structure changes, it will have to be adjusted here. currently I assume there is only 1 key
            data_key = list(response.data.keys())[0]
            body = {"data": {data_key: base64.b64encode(yaml.safe_dump(new_cluster_tap_values).encode()).decode()}}
            success, response = self.k8s_helper.patch_namespaced_secret(client=self.k8s_helper.core_clients[k8s_context], secret=tap_values_secret_name, namespace=namespace, body=body)
            if not success:
                self.logger.msg(":broken_heart: Unable to edit the configuration secret on TAP cluster. Try again later.")
                self.logger.msg(f"\n{response}", bold=False) if self.state["verbose"] else None
                raise typer.Exit(-1)

        else:
            self.logger.msg(f":broken_heart: {tap_values_secret_name} secret not found in the k8s cluster. is TAP installed properly?")
            self.logger.msg(f"\n{response}", bold=False) if self.state["verbose"] else None

    def upgrade(self, version: str, wait: bool, namespace: str = "tap-install"):
        commons.check_and_pick_k8s_context(k8s_context=None, k8s_helper=self.k8s_helper, logger=self.logger, ui_helper=self.ui_helper, state=self.state)
        # TODO: Make this configurable from tappr init
        cmd = f"tanzu package installed list --namespace {namespace}"
        _, out, _ = self.sh.run_proc(cmd=cmd)
        if "tap.tanzu.vmware.com" not in out.decode():
            self.logger.msg(":broken_heart: TAP package not found. Nothing to upgrade. Please check if TAP is installed")
            raise typer.Exit(1)

        self.sh_call(
            cmd=f"tanzu package repository update tanzu-tap-repository --url {self.install_registry_server}/tanzu-application-platform/tap-packages:{version} --namespace {namespace}",
            msg=":key: Setting up [yellow]tanzu-tap-repository[/yellow] package repo",
            spinner_msg="Setting up",
            error_msg=None,
        )
        _, out, _ = self.sh.run_proc(cmd=f"tanzu package repository get tanzu-tap-repository --namespace {namespace}")
        self.logger.msg(out.decode(), bold=False) if self.state["verbose"] and out else None

        self.sh_call(
            cmd=f"tanzu package installed update tap -p tap.tanzu.vmware.com -v {version} -n {namespace} --wait={'false' if not wait else 'true'}",
            msg=f":wine_glass: Updating [yellow]TAP[/yellow] to version [yellow]{version}[/yellow]",
            spinner_msg="Updating. Waiting to reconcile",
            error_msg=None,
        )
        if wait:
            self.logger.msg(":rocket: TAP is upgraded")
        else:
            self.logger.msg(":rocket: TAP upgrade started on the cluster")

    def uninstall(self, package: str, namespace: str = "tap-install"):
        commons.check_and_pick_k8s_context(k8s_context=None, k8s_helper=self.k8s_helper, logger=self.logger, ui_helper=self.ui_helper, state=self.state)
        self.sh_call(
            cmd=f"tanzu package installed delete {package} --namespace {namespace} --yes",
            msg=f":wine_glass: Uninstalling [yellow]TAP[/yellow]",
            spinner_msg="Deleting package",
            error_msg=None,
        )
        self.logger.msg(":rocket: TAP is uninstalled")

    def status(self, namespace: str = "tap-install"):
        k8s_context = commons.check_and_pick_k8s_context(k8s_context=None, k8s_helper=self.k8s_helper, logger=self.logger, ui_helper=self.ui_helper, state=self.state)
        success, response = self.k8s_helper.list_namespaced_custom_objects(
            group="packaging.carvel.dev",
            version="v1alpha1",
            namespace=namespace,
            plural="packageinstalls",
            client=self.k8s_helper.custom_clients[k8s_context],
        )
        if success:
            errs = list()
            for item in response["items"]:
                if "status" in item:
                    if item["status"]["conditions"][0]["type"] == "ReconcileSucceeded":
                        rprint(f":package: {item['metadata']['name']} [cyan]{item['status']['version']}[/cyan] has [bold][green]Reconciled[/green][/bold]")
                    elif item["status"]["conditions"][0]["type"] == "Reconciling":
                        rprint(f":package: {item['metadata']['name']} [cyan]{item['status']['version']}[/cyan] is [bold][yellow]Reconciling[/yellow][/bold]")
                    elif item["status"]["conditions"][0]["type"] == "Deleting":
                        rprint(f":package: {item['metadata']['name']} [cyan]{item['status']['version']}[/cyan] is [bold][yellow]Reconciling[/yellow][/bold]")
                    else:
                        errs.append([item["metadata"]["name"], item["status"]["version"], item["status"]["conditions"][0]["type"], item["status"]])
            if len(errs) > 0:
                self.console.rule("Errors")
            for err in errs:
                rprint(f":worried: {err[0]} [cyan]{err[1]}[/cyan] [bold][red]{err[2]}[/red][/bold]")
                if "usefulErrorMessage" in err[3]:
                    rprint(f"[bold][red]Error:[/red][/bold] {err[3]['usefulErrorMessage']}")
