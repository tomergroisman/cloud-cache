import boto3
import requests

from utils import get_instance_id, filter_healthy, sort_by_id, get_target_id

VPC_PORT = 8081

class EC2_Client:
  def __init__(self):
    self.client = boto3.client("ec2")
    self.elb_client = boto3.client("elbv2")
    self.instance_id = get_instance_id()

    target_groups = self.elb_client.describe_target_groups(Names=["cache-elb-tg"])
    self.target_group_arn = target_groups["TargetGroups"][0]["TargetGroupArn"]

  def get_healthy_nodes(self):
    """Get all the healthy nodes"""
    all_targets = self.elb_client.describe_target_health(TargetGroupArn=self.target_group_arn)["TargetHealthDescriptions"]
    healthy_targets = list(filter(filter_healthy, all_targets))
    sorted_healthy_targets = sort_by_id(healthy_targets)
    return healthy_targets

  def put(self, target_node, str_key, data, expiration_date):
    """Put value to provided node cache"""
    target_node_id = get_target_id(target_node)
    node_ip = self.client.describe_instances(InstanceIds=[target_node_id])["Reservations"][0]["Instances"][0]["PrivateIpAddress"]
    
    url = f"http://{node_ip}:{VPC_PORT}/put"
    res = requests.post(url, params={
      "str_key": str_key,
      "data": data,
      "expiration_date": expiration_date,
    })

    return res.text

  def get(self, target_node, str_key):
    """Get value from relevant node cache"""
    target_node_id = get_target_id(target_node)
    node_ip = self.client.describe_instances(InstanceIds=[target_node_id])["Reservations"][0]["Instances"][0]["PrivateIpAddress"]

    url = f"http://{node_ip}:{VPC_PORT}/get"
    res = requests.get(url, params={
      "str_key": str_key
    })

    return res.text

  def get_cache(self, target_node):
    """Get all values from relevant node cache"""
    target_node_id = get_target_id(target_node)
    node_ip = self.client.describe_instances(InstanceIds=[target_node_id])["Reservations"][0]["Instances"][0]["PrivateIpAddress"]

    url = f"http://{node_ip}:{VPC_PORT}/cache"
    res = requests.get(url)

    if res.status_code != 200:
      return None

    return res.json()
