from flask import Flask, Response, request
from xxhash import xxh64

from client import ELB_Client

app = Flask(__name__)
elb_client = ELB_Client()

N_VIRTUAL_NODES = 1024

@app.route("/put")
def put_to_cache():
    str_key = request.args.get('str_key', default="")
    data = request.args.get('data', default=None)
    expiration_date = request.args.get('expiration_date', default=None)

    hash_value = xxh64(str_key).intdigest()
    healthy_nodes = elb_client.get_healthy_nodes()
    v_node_idx = hash_value % N_VIRTUAL_NODES

    target_node = healthy_nodes[v_node_idx % len(healthy_nodes)]
    alt_target_node = healthy_nodes[(v_node_idx + 1) % len(healthy_nodes)]

    # TODO: Implement def put()
    # error = None
    # try:
    #     return put(target_node, str_key, data, expiration_date)
    # except e:
    #     error = e
    # return put(alt_target_node, str_key, data, expiration_date)
    # raise error if error is nor None

    return str(f"hash_value: {hash_value}, target_node_idx: {target_node_idx}, alt_target_node_idx: {alt_target_node_idx}, alinstance_id: {elb_client.instance_id}")

@app.route("/get")
def get_from_cache():
    return "in get"

@app.route("/health-check")
def health_check():
    return Response(status=200)
