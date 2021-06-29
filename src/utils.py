import urllib.request
import functools

AWS_GET_INSTANCE_ID_ENDPOINT = "http://169.254.169.254/latest/meta-data/instance-id"

def get_instance_id():
  """Get the current instance id"""
  instance_id = urllib.request.urlopen(AWS_GET_INSTANCE_ID_ENDPOINT).read().decode()
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
  other_targets = [target for target in targets if not get_target_id(target) == instance_id]
  return list(filter(filter_healthy, other_targets))

def get_my_node_idx(targets):
  """Filter other healthy targets, beside current target"""
  instance_id = get_instance_id()
  for idx, target in enumerate(targets):
    if get_target_id(target) == instance_id:
      return idx
  return -1

def update_nodes(client, buckets):
  healthy_nodes = client.get_healthy_nodes()
  n_healthy_nodes = len(healthy_nodes)
  if healthy_nodes_change(buckets, n_healthy_nodes):
      for node in healthy_nodes:
          client.update_buckets(node)
  
def healthy_nodes_change(buckets, n_healthy_nodes):
  if buckets['n_healthy_nodes'] != n_healthy_nodes:
    return True    
