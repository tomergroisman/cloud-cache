import boto3

from utils import get_instance_id, filter_other_healthy

elb_client = boto3.client('elbv2')
target_group_arn = 'arn:aws:elasticloadbalancing:eu-central-1:217568182542:targetgroup/Instances/0994232bb9fdf1f8'
instance_id = get_instance_id()

def get_healthy_targets():
  all_targets = elb_client.describe_target_health(TargetGroupArn=target_group_arn)['TargetHealthDescriptions']
  healthy_targets = filter_other_healthy(instance_id, all_targets)
  return healthy_targets

print(get_healthy_targets())
