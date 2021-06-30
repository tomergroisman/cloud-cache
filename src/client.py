import boto3
import requests
import json

from utils import (
    get_instance_id,
    filter_healthy,
    sort_by_id,
    get_target_id,
    healthy_nodes_change,
    update_buckets as utils_update_buckets
)

ELB_PORT = 8080
VPC_PORT = 8081


class EC2_Client:
    def __init__(self):
        self.client = boto3.client("ec2")
        self.elb_client = boto3.client("elbv2")
        self.instance_id = get_instance_id()

        target_groups = self.elb_client.describe_target_groups(
            Names=["cache-elb-tg"]
        )
        self.target_group_arn = \
            target_groups["TargetGroups"][0]["TargetGroupArn"]

    def get_healthy_nodes(self):
        """Get all the healthy nodes"""
        all_targets = self.elb_client.describe_target_health(
            TargetGroupArn=self.target_group_arn
        )["TargetHealthDescriptions"]
        healthy_targets = list(filter(filter_healthy, all_targets))
        sorted_healthy_targets = sort_by_id(healthy_targets)
        return sorted_healthy_targets

    def get_node_ip(self, node_id):
        """Get the ip of a node"""
        return self.client.describe_instances(
            InstanceIds=[node_id]
        )["Reservations"][0]["Instances"][0]["PrivateIpAddress"]

    def put(self, target_node, bucket_idx, str_key, data, expiration_date):
        """Put value to provided node cache"""
        target_node_id = get_target_id(target_node)
        node_ip = self.get_node_ip(target_node_id)

        url = f"http://{node_ip}:{VPC_PORT}/put"
        res = requests.post(url, params={
            "n_bucket": bucket_idx,
            "str_key": str_key,
            "data": data,
            "expiration_date": expiration_date,
        })

        if res.status_code != 200:
            raise requests.exceptions.RequestException

        return res.text

    def get(self, target_node, bucket_idx, str_key):
        """Get value from relevant node cache"""
        target_node_id = get_target_id(target_node)
        node_ip = self.get_node_ip(target_node_id)

        url = f"http://{node_ip}:{VPC_PORT}/get"
        res = requests.get(url, params={
            "n_bucket": bucket_idx,
            "str_key": str_key
        })

        if res.status_code != 200:
            raise requests.exceptions.RequestException

        return res.text

    def get_cache(self, target_node):
        """Get all values from relevant node cache"""
        target_node_id = get_target_id(target_node)
        node_ip = self.get_node_ip(target_node_id)

        url = f"http://{node_ip}:{VPC_PORT}/cache"
        res = requests.get(url)

        if res.status_code != 200:
            return "ERROR", 400

        return res.json()

    def update_nodes(self, buckets, n_v_nodes):
        """Trigger node update in case of healthy nodes change"""
        healthy_nodes = self.get_healthy_nodes()
        n_healthy_nodes = len(healthy_nodes)

        if healthy_nodes_change(buckets, n_healthy_nodes):
            buckets = utils_update_buckets(
                buckets, n_healthy_nodes, n_v_nodes, healthy_nodes
            )
            for idx, node in enumerate(healthy_nodes):
                try:
                    self.update_buckets(node, buckets)
                except Exception:
                    print(f"Unable to update buckets for node of index {idx}")

    def update_buckets(self, target_node, buckets):
        """Trigger a node to update its buckets list"""
        target_node_id = get_target_id(target_node)
        node_ip = self.get_node_ip(target_node_id)

        url = f"http://{node_ip}:{ELB_PORT}/update_buckets"
        res = requests.post(url, data=json.dumps({
            'buckets': buckets
        }))

        if res.status_code != 200:
            raise requests.exceptions.RequestException

        return "Success"

    def delete_and_send(self, bucket_idx, node_ip, alt_node_ip):
        """Self request to delete a bucket and put it in its new owners"""
        my_ip = self.get_node_ip(get_instance_id())

        url = f"http://{my_ip}:{VPC_PORT}/delete_and_send"
        res = requests.post(url, params={
            'node_ip': node_ip,
            'alt_node_ip': alt_node_ip,
            'n_bucket': bucket_idx
        })

        if res.status_code != 200:
            raise requests.exceptions.RequestException

        return "Success"

    def copy(self, source_node, target_node):
        """Request a source node to copy its cache to target node"""
        source_node_id = get_target_id(source_node)
        source_node_ip = self.get_node_ip(source_node_id)

        target_node_id = get_target_id(target_node)
        target_node_ip = self.get_node_ip(target_node_id)

        url = f"http://{source_node_ip}:{VPC_PORT}/copy"
        res = requests.post(url, params={
            "target_node_id": target_node_id,
            "target_node_ip": target_node_ip
        })

        if res.status_code != 200:
            raise requests.exceptions.RequestException

        return "Success"

    def send_bucket(self, target_node_id, bucket_idx):
        """Request a target node to copy a bucket"""
        target_node_ip = self.get_node_ip(target_node_id)

        url = f"http://{target_node_ip}:{VPC_PORT}/send-bucket"
        res = requests.post(url, params={
            "node_ip": target_node_ip,
            "n_bucket": bucket_idx
        })

        if res.status_code != 200:
            raise requests.exceptions.RequestException

        return "Success"
