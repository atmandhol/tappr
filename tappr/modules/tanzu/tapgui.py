import os
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
