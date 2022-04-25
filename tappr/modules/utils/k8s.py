import kubernetes as k8s
from kubernetes.client.rest import ApiException
from tappr.modules.utils.ui import Picker


# noinspection PyBroadException,PyTypeChecker
class K8s:
    def __init__(self):
        self.config = k8s.config
        self.client = k8s.client
        self.current_context = str()
        self.contexts: list[str] = list()
        self.current_core_client: k8s.client.CoreV1Api = None
        self.core_clients: dict[str, k8s.client.CoreV1Api] = dict()
        self.current_custom_client: k8s.client.CustomObjectsApi = None
        self.custom_clients: dict[str, k8s.client.CustomObjectsApi] = dict()
        self.load_contexts_and_clients()

    def load_contexts_and_clients(self):
        # Adding try/catch block so that tappr init does not blow up if the KUBECONFIG has no clusters/entries
        try:
            contexts_obj, current_context = self.config.list_kube_config_contexts()
            # Set currents
            self.current_context = current_context.get("name")
            self.current_core_client = self.client.CoreV1Api(api_client=self.config.new_client_from_config(context=self.current_context))
            self.current_custom_client = self.client.CustomObjectsApi(api_client=self.config.new_client_from_config(context=self.current_context))
            # Set all
            for ctx in contexts_obj:
                self.contexts.append(ctx["name"])
                self.core_clients[ctx["name"]] = self.client.CoreV1Api(api_client=self.config.new_client_from_config(context=ctx["name"]))
                self.custom_clients[ctx["name"]] = self.client.CustomObjectsApi(api_client=self.config.new_client_from_config(context=ctx["name"]))
        except Exception:
            pass

    def create_namespace(self, namespace, client=None):
        """
        return success:bool, obj: kubernetes.client.models.v1_namespace.V1Namespace/kubernetes.client.exceptions.ApiException
        """
        client = self.current_core_client if not client else client
        try:
            response = client.create_namespace(k8s.client.V1Namespace(api_version="v1", kind="Namespace", metadata={"name": namespace}))
            return True, response
        except ApiException as err:
            return False, err

    def get_namespaced_secret(self, client, secret, namespace):
        client = self.current_core_client if not client else client
        try:
            response = client.read_namespaced_secret(name=secret, namespace=namespace)
            return True, response
        except ApiException as err:
            return False, err

    def patch_namespaced_secret(self, client, secret, namespace, body):
        client = self.current_core_client if not client else client
        try:
            response = client.patch_namespaced_secret(name=secret, namespace=namespace, body=body)
            return True, response
        except ApiException as err:
            return False, err

    def get_namespaced_service(self, service, namespace, client=None):
        client = self.current_core_client if not client else client
        try:
            response = client.read_namespaced_service(name=service, namespace=namespace)
            return True, response
        except ApiException as err:
            return False, err

    def pick_context(self):
        options = self.contexts
        try:
            # We do a try here because if you delete a cluster which was the current context and don't switch your current
            # context before running anything that needs to call pick_context, the remove will fail as it will no longer be in the contexts list.
            options.remove(self.current_context)
        except Exception:
            pass
        options.append(self.current_context)
        if len(options) > 1:
            option, _ = Picker(options, "Pick k8s context (Last one in the list is the current context):").start()
        else:
            return self.current_context
        return option

    def pick_multiple_contexts(self):
        options = self.contexts
        options.remove(self.current_context)
        options.append(self.current_context)
        if len(options) > 1:
            selected = Picker(
                options, "Pick k8s context (Last one in the list is the current context):", multiselect=True, min_selection_count=1
            ).start()
        else:
            return [self.current_context]
        return selected

    def list_namespaced_custom_objects(self, group, version, namespace, plural, client=None):
        client = self.current_custom_client if not client else client
        try:
            response = client.list_namespaced_custom_object(group=group, version=version, namespace=namespace, plural=plural)
            return True, response
        except ApiException as err:
            return False, err

    def get_namespaced_custom_objects(self, name, group, version, namespace, plural, client=None):
        client = self.current_custom_client if not client else client
        try:
            response = client.get_namespaced_custom_object(group=group, version=version, namespace=namespace, plural=plural, name=name)
            return True, response
        except ApiException as err:
            return False, err
