from kubernetes import client, config
from pick import pick
import json


class ScalePods:
    def __init__(self, cluster, namespace):
        config.load_kube_config()
        self.cluster = cluster
        self.namespace = namespace
        self.filename = "replica_counts_" + cluster + ".json"
        self.v1 = client.AppsV1Api(api_client=config.new_client_from_config(context=cluster))
        self.deployments = self.v1.list_namespaced_deployment(namespace)

    def scale_down(self):
        print("Scaling down")

        for deploy in self.deployments.items:
            name = deploy.metadata.name
            self.v1.patch_namespaced_deployment_scale(name, self.namespace, {"spec": {"replicas": 0}})
            print(f"Scaled down {self.namespace}/{name} to 0 replicas")

    def scale_up(self):
        print("Scaling up")

        with open(self.filename, "r") as fn:
            replica_file = fn.read()

        replicas = json.loads(replica_file)

        for deploy in self.deployments.items:
            name = deploy.metadata.name
            replica_count = replicas.get(name)
            self.v1.patch_namespaced_deployment_scale(name, self.namespace, {"spec": {"replicas": replica_count}})
            print(f"Scaled up {self.namespace}/{name} to {replica_count} replicas")

    # Gather deployment data and store for scaling up later
    def fetch_replicas(self):
        print("Fetching replicas")
        replica_counts = {}

        for deployment in self.deployments.items:
            name = deployment.metadata.name
            replicas = deployment.spec.replicas
            replica_counts[name] = replicas

        deployment_count = len(replica_counts)
        replica_sum = sum(replica_counts.values)
        if deployment_count == 0 or replica_sum == 0:
            process, proc_index = pick(['No', 'Yes'], title="No deployments to store. Continue?", default_index=0)
            if process == 'No':
                return False
        with open(self.filename, "w") as fn:
            json.dump(replica_counts, fn)

        print(f"Original replica counts stored locally in {self.filename}")
        return True
    