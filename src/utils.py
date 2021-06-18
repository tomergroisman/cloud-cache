import urllib.request

AWS_GET_INSTANCE_ID_ENDPOINT = "http://169.254.169.254/latest/meta-data/instance-id"

def get_instance_id():
  instance_id = urllib.request.urlopen(AWS_GET_INSTANCE_ID_ENDPOINT).read().decode()
  return instance_id

def filter_healthy(target):
  return target["TargetHealth"]["State"] == "healthy"

def filter_other_healthy(instance_id, targets):
  other_targets = [target for target in targets if not target["Target"]["Id"] == instance_id]
  return list(filter(filter_healthy, other_targets))
  
  