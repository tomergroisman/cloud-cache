from flask import Flask, Response, request
from xxhash import xxh64

from client import ELB_Client

app = Flask(__name__)
elb_client = ELB_Client()

@app.route("/put")
def put_to_cache():
    str_key = request.args.get('str_key', default="")
    data = request.args.get('data', default=None)
    expiration_date = request.args.get('expiration_date', default=None)

    hash_value = xxh64(str_key).intdigest()
    healthy_nodes = elb_client.get_healthy_nodes()
    target_node = hash_value % len(healthy_nodes)

    return str(f"hash_value: {hash_value}, target_node: {target_node}")

@app.route("/get")
def get_from_cache():
    return "in get"

@app.route("/health-check")
def health_check():
    return Response(status=200)
