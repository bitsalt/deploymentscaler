from pick import pick
from kubernetes import client, config
from ScalePods import ScalePods


class DeploymentScaler:
    process_options = [
        'check pods',
        'delete pods',
        'restore pods',
        'cancel'
    ]
    contexts = None
    active_context = None
    core_api = None
    apps_api = None
    scaler = None

    def __init__(self):
        self.contexts, self.active_context = config.list_kube_config_contexts()
        if not self.contexts:
            print('No contexts available')
            return

        self.contexts = [context['name'] for context in self.contexts]

    def main(self):
        # Offer selections
        active_index = self.contexts.index(self.active_context['name'])
        process_selected, proc_index = pick(self.process_options, title="Select a process", default_index=0)
        cluster_selected, cluster_index = pick(self.contexts, title="Select a context", default_index=active_index)

        # Create connections
        self.apps_api = client.AppsV1Api(api_client=config.new_client_from_config(context=cluster_selected))
        self.core_api = client.CoreV1Api(api_client=config.new_client_from_config(context=cluster_selected))
        self.scaler = ScalePods(cluster_selected, self.apps_api, self.core_api)

        # Route based on selections
        self.router(process_selected)

        # Clean up connections
        self.apps_api.api_client.close()
        self.apps_api.api_client.close()

    def router(self, process) -> None:

        if process == 'cancel':
            print("Cancelling")
            return

        # Select namespace
        self.get_namespace_selection()

        # Gather data
        self.scaler.fetch_deployments()
        self.scaler.fetch_replicas()

        # Route paths other than 'cancel'
        if process == 'restore pods':
            self.restore()
        if process == 'check pods':
            self.check_pods()
        if process == 'delete pods':
            self.delete_pods()

    def get_namespace_selection(self) -> None:
        namespaces = self.scaler.fetch_namespaces()
        namespace_selected, ns_index = pick(namespaces, title="Select a namespace")
        self.scaler.set_namespace(namespace_selected)

    def restore(self) -> None:
        print("Scaling up...")
        self.scaler.scale_up()
        print("Scaling complete.")

    def check_pods(self) -> None:
        title_text = f"{self.scaler.deployment_count}  deployments with {self.scaler.replica_count} replicas."
        if self.scaler.replica_file_exists():
            title_text += " WARNING: The file already exists locally! Overwrite?"
        else:
            title_text += " Write file?"
        process, proc_index = pick(['No', 'Yes'], title=title_text, default_index=0)
        if process is 'Yes':
            if self.scaler.write_replicas():
                print(f"File written: {self.scaler.filename}")
            else:
                print(f"File {self.scaler.filename} failed to write.")
        else:
            print("Closing without writing a file.")

    def delete_pods(self) -> None:
        if not self.scaler.replica_file_exists():
            if not self.scaler.write_replicas():
                print(f"File {self.scaler.filename} does not exist. Aborting!")
                return

        if self.scaler.replica_count < self.scaler.low_replica_count_threshold:
            proc_title = f"Low replica count of {self.scaler.replica_count}. Continue?"
            process, proc_index = pick(['No', 'Yes'], title=proc_title, default_index=0)
            if process is 'No':
                return

        self.scaler.scale_down()


if __name__ == "__main__":
    scaler = DeploymentScaler()
    scaler.main()
