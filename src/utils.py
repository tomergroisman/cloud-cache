import urllib.request

AWS_GET_INSTANCE_ID_ENDPOINT = \
  "http://169.254.169.254/latest/meta-data/instance-id"


def get_instance_id():
    """Get the current instance id"""
    instance_id = urllib.request.urlopen(
        AWS_GET_INSTANCE_ID_ENDPOINT
    ).read().decode()
    return instance_id


def get_target_id(target):
    """Get the target instance id"""
    return target["Target"]["Id"]


def sort_by_id(targets):
    """Sort target list by id"""
    return sorted(targets, key=get_target_id)


def filter_healthy(target):
    """Filter healthy targets from target list"""
    return target["TargetHealth"]["State"] == "healthy"


def filter_other_healthy(instance_id, targets):
    """Filter other healthy targets, beside current target"""
    other_targets = [
        tr for tr in targets if not get_target_id(tr) == instance_id
    ]
    return list(filter(filter_healthy, other_targets))


def get_my_node_idx(targets):
    """Filter other healthy targets, beside current target"""
    instance_id = get_instance_id()
    for idx, target in enumerate(targets):
        if get_target_id(target) == instance_id:
            return idx
    return -1


def healthy_nodes_change(buckets, n_healthy_nodes):
    """Check for change of healthy nodes status"""
    if buckets['n_healthy_nodes'] != n_healthy_nodes:
        return True


def update_buckets(buckets, n_healthy_nodes, n_v_nodes):
    """Update and return buckets mapping"""
    new_buckets = {
        **buckets,
        "n_healthy_nodes": n_healthy_nodes
    }
    for bucket_idx in range(len(new_buckets['mapping'])):
        new_buckets['mapping'][bucket_idx]['node'] = \
            n_v_nodes % n_healthy_nodes
        new_buckets['mapping'][bucket_idx]['alt_node'] = \
            ((n_v_nodes % n_healthy_nodes) + 1) % n_healthy_nodes
    return new_buckets
