from flask import Flask, request
import json
import requests

from cache import Node_Cache
from utils import get_instance_id
from client import VPC_PORT

app = Flask(__name__)
cache = Node_Cache()
instance_id = get_instance_id()


@app.route("/put", methods=['POST'])
def put_to_cache():
    n_bucket = request.args.get('n_bucket', -1)
    str_key = request.args.get('str_key', default="")
    data = request.args.get('data', default=None)
    expiration_date = request.args.get('expiration_date', default=None)

    try:
        cache.put(n_bucket, str_key, data, expiration_date)
    except Exception:
        return "ERROR", 400

    return f"Success, instance_id: {instance_id}\n"


@app.route("/put-bucket", methods=['POST'])
def put_bucket_to_cache():
    data = json.loads(request.data)
    n_bucket = data.get('n_bucket', -1)
    bucket_data = data.get('bucket_data', {})

    try:
        cache.put_bucket(n_bucket, bucket_data)
    except Exception:
        return "ERROR", 400

    return f"Success, instance_id: {instance_id}\n"


@app.route("/get", methods=['GET'])
def get_from_cache():
    n_bucket = request.args.get('n_bucket', -1)
    str_key = request.args.get('str_key', default="")

    data = cache.get(n_bucket, str_key)

    if not data:
        return "ERROR", 400

    return data


@app.route("/cache", methods=['GET'])
def get_cache():
    data = cache.get_cache()
    res = {
        "instance_id": instance_id,
        "cache": data
    }
    return res


@app.route("/delete_and_send", methods=['POST'])
def delete_and_send_cache():
    node_ip = request.args.get('node_ip', None)
    alt_node_ip = request.args.get('alt_node_ip', None)
    n_bucket = request.args.get('n_bucket', -1)

    bucket_data = cache.delete(n_bucket)

    if bucket_data:
        if node_ip:
            url = f"http://{node_ip}:{VPC_PORT}/put-bucket"
            requests.post(
                url,
                data=json.dumps({
                    "n_bucket": n_bucket,
                    "bucket_data": bucket_data
                }))
        if alt_node_ip:
            url = f"http://{alt_node_ip}:{VPC_PORT}/put-bucket"
            requests.post(
                url,
                data=json.dumps({
                    "n_bucket": n_bucket,
                    "bucket_data": bucket_data
                }))

        return "Success"

    return "No data in bucket", 400


@app.route("/send-bucket", methods=['POST'])
def send_bucket_from_cache():
    node_ip = request.args.get('node_ip', None)
    n_bucket = request.args.get('n_bucket', -1)

    bucket_data = cache.get_bucket(n_bucket)

    if bucket_data:
        if node_ip:
            url = f"http://{node_ip}:{VPC_PORT}/put-bucket"
            requests.post(
                url,
                data=json.dumps({
                    "n_bucket": n_bucket,
                    "bucket_data": bucket_data
                }))

        return "Success"

    return "No data in bucket", 400


@app.route("/copy", methods=['POST'])
def copy_cache():
    target_node_ip = request.args.get('target_node_ip', None)

    if target_node_ip:
        url = f"http://{target_node_ip}:{VPC_PORT}/put-cache"
        res = requests.post(
            url,
            data=json.dumps({
                "cache": cache.get_cache()
            }))

        if res.status_code != 200:
            return "Unable to copy cache", 400

        return "Success"

    return "ERROR", 400


@app.route("/put-cache", methods=['POST'])
def put_cache():
    new_cache = json.loads(request.data).get('cache', {})

    try:
        cache.put_cache(new_cache)
    except Exception:
        return "Unable to put new cache", 400

    return "Success"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, debug=True)
