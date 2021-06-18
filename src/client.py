import boto3

from utils import get_instance_id, filter_healthy, sort_by_id

target_group_arn = "arn:aws:elasticloadbalancing:eu-central-1:217568182542:targetgroup/Instances/0994232bb9fdf1f8"

class ELB_Client:
  def __init__(self):
    self.client = boto3.client("elbv2")
    self.instance_id = get_instance_id()

  def get_healthy_nodes(self):
    all_targets = self.client.describe_target_health(TargetGroupArn=target_group_arn)["TargetHealthDescriptions"]
    healthy_targets = list(filter(filter_healthy, all_targets))
    sorted_healthy_targets = sort_by_id(healthy_targets)
    return healthy_targets
