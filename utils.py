import urllib.request

def get_instance_id():
  instance_id = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read().decode()
  return instance_id

def filter_other_healthy(instance_id, targets):
  def filter_healthy(target):
    return target['TargetHealth']['State'] == 'healthy' and not target['Target']['Id'] == instance_id

  return list(filter(filter_healthy, targets))
  
  