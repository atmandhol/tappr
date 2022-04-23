import kubernetes as k8s
from kubernetes.client.rest import ApiException
from tappr.modules.utils.ui import Picker


class K8s:
    def __init__(self):
        self.config = k8s.config
        self.client = k8s.client
        self.current_context = str()
        self.contexts = list()
        self.current_client = None
        self.clients = dict()
        self.load_contexts_and_clients()

    def load_contexts_and_clients(self):
        contexts_obj, current_context = self.config.list_kube_config_contexts()
        # Set currents
        self.current_context = current_context.get("name")
        self.current_client = self.client.CoreV1Api(api_client=self.config.new_client_from_config(context=self.current_context))

        # Set all
        for ctx in contexts_obj:
            self.contexts.append(ctx["name"])
            self.clients[ctx["name"]] = self.client.CoreV1Api(api_client=self.config.new_client_from_config(context=ctx["name"]))

    def create_namespace(self, namespace, client=None):
        """
        return success:bool, obj: kubernetes.client.models.v1_namespace.V1Namespace/kubernetes.client.exceptions.ApiException
        """
        client = self.current_client if not client else client
        try:
            response = client.create_namespace(k8s.client.V1Namespace(api_version="v1", kind="Namespace", metadata={"name": namespace}))
            return True, response
        except ApiException as err:
            return False, err

    def get_namespaced_secret(self, client, secret, namespace):
        client = self.current_client if not client else client
        try:
            response = client.read_namespaced_secret(name=secret, namespace=namespace)
            return True, response
        except ApiException as err:
            return False, err

    def pick_context(self):
        options = self.contexts
        options.remove(self.current_context)
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
