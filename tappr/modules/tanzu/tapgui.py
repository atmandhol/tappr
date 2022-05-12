import os
import base64
import typer
import yaml

import tappr.modules.utils.k8s
from tappr.modules.utils.commons import Commons

commons = Commons()


# noinspection PyBroadException
class TanzuApplicationPlatformGUI:
    def __init__(self, subprocess_helper, pivnet_helper, logger, creds_helper, state, ui_helper, k8s_helper, console):
        self.console = console
        self.creds_helper = creds_helper
        self.logger = logger
        self.sh = subprocess_helper
        self.pivnet_helpers = pivnet_helper
        self.state = state
        self.ui_helper = ui_helper
        self.k8s_helper: tappr.modules.utils.k8s.K8s = k8s_helper

    def sh_call(self, cmd, msg, spinner_msg, error_msg):
        return self.ui_helper.sh_call(cmd=cmd, msg=msg, spinner_msg=spinner_msg, error_msg=error_msg, state=self.state)

    def server_ip(self, service: str, namespace: str):
        k8s_context = commons.check_and_pick_k8s_context(
            k8s_context=None, k8s_helper=self.k8s_helper, logger=self.logger, ui_helper=self.ui_helper, state=self.state
        )
        success, response = self.k8s_helper.get_namespaced_service(
            service=service, namespace=namespace, client=self.k8s_helper.core_clients[k8s_context]
        )
        if success:
            try:
                # This fails when you try to get a public ip when contour is not installed as load balancer,
                # or you are trying to do this in a build cluster
                for ingress in response.status.load_balancer.ingress:
                    print(ingress.ip)
            except Exception:
                self.logger.msg(":broken_heart: No external TAP GUI server IP found")
        else:
            self.logger.msg(":broken_heart: No external TAP GUI server IP found")
            self.logger.msg(f"\n{response}", bold=False) if self.state["verbose"] else None

    def track_cluster(self, namespace):
        k8s_context = commons.check_and_pick_k8s_context(
            k8s_context=None,
            k8s_helper=self.k8s_helper,
            logger=self.logger,
            ui_helper=self.ui_helper,
            state=self.state,
            pick_message="Select a TAP cluster to add to TAP GUI",
        )
        source_cluster_name = self.logger.question("What do want to call this cluster on TAP GUI", default=k8s_context)
        source_namespace = commons.pick_namespace(k8s_helper=self.k8s_helper, client=self.k8s_helper.core_clients[k8s_context])

        success, source_sa = self.k8s_helper.get_namespaced_service_account(
            client=self.k8s_helper.core_clients[k8s_context], service_account="tap-gui-viewer", namespace=source_namespace
        )
        if not success:
            # TODO: Throw error, be nice to user etc
            raise typer.Exit(-1)

        source_secret_name = None
        try:
            source_secret_name = source_sa.secrets[0].name
        except Exception:
            # TODO Throw error, cannot find secret etc.
            pass

        success, secret = self.k8s_helper.get_namespaced_secret(
            client=self.k8s_helper.core_clients[k8s_context], secret=source_secret_name, namespace=source_namespace
        )

        if not success:
            # TODO: Throw error, be nice to user etc
            raise typer.Exit(-1)

        cluster_token = ""
        try:
            cluster_token = base64.b64decode(secret.data.get("token")).decode()
        except Exception:
            # TODO Throw error, cannot find token etc.
            pass

        _, cluster_url, _ = self.sh.run_proc(cmd="kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}'")
        cluster_url = cluster_url.decode()

        k8s_context = commons.check_and_pick_k8s_context(
            k8s_context=None,
            k8s_helper=self.k8s_helper,
            logger=self.logger,
            ui_helper=self.ui_helper,
            state=self.state,
            pick_message="Select a TAP cluster with TAP GUI installed where you would like to track:",
        )

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

        success, response = self.k8s_helper.get_namespaced_secret(
            secret=tap_values_secret_name, namespace=namespace, client=self.k8s_helper.core_clients[k8s_context]
        )

        if not success:
            # TODO: Throw error, be nice to user etc
            raise typer.Exit(-1)

        if success:
            try:
                tap_values = yaml.safe_load(base64.b64decode(list(response.data.values())[0]).decode())
                og_tap_values = yaml.safe_load(base64.b64decode(list(response.data.values())[0]).decode())
            except Exception:
                self.logger.msg(f":cry: {tap_values_secret_name} secret was not proper yaml")
                raise typer.Exit(1)

            try:
                _ = tap_values["tap_gui"] and tap_values["tap_gui"]["app_config"]
            except KeyError:
                self.logger.msg(f":cry: tap_gui or app_config not found in TAP values file")
                raise typer.Exit(-1)

            if not hasattr(tap_values["tap_gui"]["app_config"], "kubernetes"):
                tap_values["tap_gui"]["app_config"]["kubernetes"] = dict()
            if not hasattr(tap_values["tap_gui"]["app_config"]["kubernetes"], "clusterLocatorMethods"):
                tap_values["tap_gui"]["app_config"]["kubernetes"]["clusterLocatorMethods"] = [dict()]
            if not hasattr(tap_values["tap_gui"]["app_config"]["kubernetes"]["clusterLocatorMethods"][0], "clusters"):
                tap_values["tap_gui"]["app_config"]["kubernetes"]["clusterLocatorMethods"][0]["clusters"] = list()
            if not hasattr(tap_values["tap_gui"]["app_config"]["kubernetes"]["clusterLocatorMethods"][0], "type"):
                tap_values["tap_gui"]["app_config"]["kubernetes"]["clusterLocatorMethods"][0]["type"] = "config"

            tap_values["tap_gui"]["app_config"]["kubernetes"]["clusterLocatorMethods"][0]["clusters"].append(
                {
                    "authProvider": "serviceAccount",
                    "name": f"{source_cluster_name}-{source_namespace}",
                    "serviceAccountToken": f"{cluster_token}",
                    "skipTLSVerify": True,
                    "url": f"{cluster_url}",
                }
            )
            commons.print_smart_diff(og_tap_values, tap_values)
            # hack: TODO: if the data object structure changes, it will have to be adjusted here. currently I assume there is only 1 key
            data_key = list(response.data.keys())[0]
            body = {"data": {data_key: base64.b64encode(yaml.safe_dump(tap_values).encode()).decode()}}
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
