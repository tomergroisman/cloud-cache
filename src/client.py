import boto3
import requests

from utils import get_instance_id, filter_healthy, sort_by_id

target_group_arn = "arn:aws:elasticloadbalancing:eu-central-1:217568182542:targetgroup/Instances/0994232bb9fdf1f8"
VPC_PORT = 8080

class EC2_Client:
  def __init__(self):
    self.client = boto3.client("ec2")
    self.elb_client = boto3.client("elbv2")
    self.instance_id = get_instance_id()

  def get_healthy_nodes(self):
    all_targets = self.elb_client.describe_target_health(TargetGroupArn=target_group_arn)["TargetHealthDescriptions"]
    healthy_targets = list(filter(filter_healthy, all_targets))
    sorted_healthy_targets = sort_by_id(healthy_targets)
    return healthy_targets

  def put(target_node, str_key, data, expiration_date):
    target_node_id = get_target_id(target_node)
    node_ip = client.describe_instances(InstanceIds=[target_node_id])["Reservations"][0]["Instances"][0]["PrivateIpAddress"]
    
    url = f"{node_ip}:{VPC_PORT}"
    res = requests.post(url, params={
      "str_key": str_key,
      "data": data,
      "expiration_date": expiration_date,
    })

    return res.text

  def get(target_node, str_key):
    target_node_id = get_target_id(target_node)
    node_ip = client.describe_instances(InstanceIds=[target_node_id])["Reservations"][0]["Instances"][0]["PrivateIpAddress"]

    url = f"{node_ip}:{VPC_PORT}"
    res = requests.get(url, params={
      "str_key": str_key
    })

    return res.text
