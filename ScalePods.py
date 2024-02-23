import json
import os


class ScalePods:
    def __init__(self, cluster: str, apps_api, core_api) -> None:
        self.cluster = cluster
        self.namespace = None
        self.filename = None
        self.deployments = {}
        self.replicas = {}
        self.replica_count = 0
        self.deployment_count = 0
        self.low_replica_count_threshold = 10
        self.v1AppsApi = apps_api
        self.v1CoreApi = core_api

    def count_replicas(self) -> int:
        return self.replica_count

    # Get deployments for selected namespace. Note: this cannot be called before
    # a namespace is selected.
    def fetch_deployments(self) -> None:
        if not self.namespace:
            print("Namespace must be selected before fetching deployments. Aborting!")
            exit()

        self.deployments = self.v1AppsApi.list_namespaced_deployment(self.namespace)
        self.deployment_count = len(self.deployments.items)

    def fetch_namespaces(self) -> list:
        namespaces = self.v1CoreApi.list_namespace()
        ns_list = []
        for ns in namespaces.items:
            ns_list.append(ns.metadata.name)

        return ns_list

    # Gather deployment data and store for scaling up later
    def fetch_replicas(self) -> None:
        for deployment in self.deployments.items:
            name = deployment.metadata.name
            replica_num = deployment.spec.replicas
            self.replicas[name] = replica_num
            self.replica_count += replica_num

    def is_valid_replica(self) -> bool:
        if self.replica_count == 0:
            return False

        return True

    def replica_file_exists(self) -> bool:
        return os.path.isfile(self.filename)

    def scale_down(self) -> None:
        print("Scaling down...")
        for deploy in self.deployments.items:
            name = deploy.metadata.name
            self.v1AppsApi.patch_namespaced_deployment_scale(name, self.namespace, {"spec": {"replicas": 0}})
            print(f"Scaled down {self.namespace}/{name} to 0 replicas")

    def scale_up(self) -> None:
        print("Scaling up...")
        with open(self.filename, "r") as fn:
            replica_file = fn.read()

        replicas = json.loads(replica_file)

        for deploy in self.deployments.items:
            name = deploy.metadata.name
            replica_count = replicas.get(name)
            self.v1AppsApi.patch_namespaced_deployment_scale(name, self.namespace, {"spec": {"replicas": replica_count}})
            print(f"Scaled up {self.namespace}/{name} to {replica_count} replicas")

    def set_filename(self) -> None:
        self.filename = "data/replicas_" + self.cluster + "_" + self.namespace + ".json"

    def set_namespace(self, namespace: str) -> None:
        self.namespace = namespace
        self.set_filename()

    def write_replicas(self) -> bool:
        if self.replica_count == 0:
            print("No replicas to write to file.")
            return False

        with open(self.filename, "w") as fn:
            json.dump(self.replicas, fn)
        return self.replica_file_exists()
