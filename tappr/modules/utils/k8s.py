import yaml
import kubernetes as k8s

from kubernetes.client.rest import ApiException
from tappr.modules.utils.ui import Picker
from tappr.modules.utils.logger import TyperLogger


# noinspection PyBroadException,PyTypeChecker
class K8s:
    def __init__(self, state=None, logger=None):
        self.state = {"verbose": False} if state is None else state
        self.logger = TyperLogger() if logger is None else logger
        self.config = k8s.config
        self.client = k8s.client
        self.contexts: list[str] = list()
        self.core_clients: dict[str, k8s.client.CoreV1Api] = dict()
        self.custom_clients: dict[str, k8s.client.CustomObjectsApi] = dict()
        self.load_contexts_and_clients()

    def load_contexts_and_clients(self):
        # Adding try/catch block so that tappr init does not blow up if the KUBECONFIG has no clusters/entries
        try:
            contexts_obj, current_context = self.config.list_kube_config_contexts()
            for ctx in contexts_obj:
                try:
                    self.core_clients[ctx["name"]] = self.client.CoreV1Api(api_client=self.config.new_client_from_config(context=ctx["name"]))
                    self.custom_clients[ctx["name"]] = self.client.CustomObjectsApi(
                        api_client=self.config.new_client_from_config(context=ctx["name"])
                    )
                    self.contexts.append(ctx["name"])
                except Exception:
                    pass
        except Exception:
            pass

    @staticmethod
    def create_namespace(namespace, client=None):
        """
        return success:bool, obj: kubernetes.client.models.v1_namespace.V1Namespace/kubernetes.client.exceptions.ApiException
        """
        try:
            response = client.create_namespace(k8s.client.V1Namespace(api_version="v1", kind="Namespace", metadata={"name": namespace}))
            return True, response
        except ApiException as err:
            return False, err

    @staticmethod
    def get_namespaced_secret(client, secret, namespace):
        try:
            response = client.read_namespaced_secret(name=secret, namespace=namespace)
            return True, response
        except ApiException as err:
            return False, err

    @staticmethod
    def patch_namespaced_secret(client, secret, namespace, body):
        try:
            response = client.patch_namespaced_secret(name=secret, namespace=namespace, body=body)
            return True, response
        except ApiException as err:
            return False, err

    @staticmethod
    def get_namespaced_service(service, namespace, client=None):
        try:
            response = client.read_namespaced_service(name=service, namespace=namespace)
            return True, response
        except ApiException as err:
            return False, err

    def pick_context(self):
        options = self.contexts
        if len(options) == 0:
            return ""
        if len(options) > 1:
            option, _ = Picker(options, "Pick k8s context (Last one in the list is the current context):").start()
        else:
            return options[0]
        return option

    def pick_multiple_contexts(self):
        options = self.contexts
        if len(options) == 0:
            return []
        if len(options) > 1:
            selected = Picker(
                options, "Pick k8s context (Last one in the list is the current context):", multiselect=True, min_selection_count=1
            ).start()
        else:
            return [options[0]]
        return selected

    @staticmethod
    def list_namespaced_custom_objects(group, version, namespace, plural, client=None):
        try:
            response = client.list_namespaced_custom_object(group=group, version=version, namespace=namespace, plural=plural)
            return True, response
        except ApiException as err:
            return False, err

    @staticmethod
    def get_namespaced_custom_objects(name, group, version, namespace, plural, client=None):
        try:
            response = client.get_namespaced_custom_object(group=group, version=version, namespace=namespace, plural=plural, name=name)
            return True, response
        except ApiException as err:
            return False, err

    @staticmethod
    def create_namespaced_custom_objects(yml, namespace: str = "default", client=None):
        # Any file in the template directory will expect the first line to be of this format
        # $$group,version,plural$$
        try:
            components = yml.split("\n")[0].split("$$")[1].split(",")
            group = components[0]
            version = components[1]
            plural = components[2]
        except Exception as err:
            return False, err

        try:
            response = client.create_namespaced_custom_object(group=group, version=version, namespace=namespace, plural=plural, body=yml)
            return True, response
        except ApiException as err:
            return False, err
