from pick import pick
from kubernetes import client, config
from ScalePods import ScalePods


def main():
    namespace = 'namespace-goes-here'
    contexts, active_context = config.list_kube_config_contexts()

    if not contexts:
        print('No contexts available')
        return

    contexts = [context['name'] for context in contexts]
    active_index = contexts.index(active_context['name'])
    cluster_name, cluster_index = pick(contexts, title="Select a context", default_index=active_index)
    process, proc_index = pick(['delete pods', 'restore pods', 'cancel'], title="Select a process", default_index=0)
    scaler = ScalePods(cluster_name, namespace)

    if process == 'cancel':
        print("Cancelling")
        exit(0)
    elif process == 'restore pods':
        scaler.scale_up()
    else:
        deployments_stored = scaler.fetch_replicas()
        if not deployments_stored:
            print("No deployments. Aborting!")
            exit()
        scaler.scale_down()


if __name__ == "__main__":
    main()
