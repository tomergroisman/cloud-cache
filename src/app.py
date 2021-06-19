import json
from flask import Flask, Response, request
from xxhash import xxh64

from client import EC2_Client

app = Flask(__name__)
client = EC2_Client()

N_VIRTUAL_NODES = 1024

@app.route("/put")
def put_to_cache():
    str_key = request.args.get('str_key', default="")
    data = request.args.get('data', default=None)
    expiration_date = request.args.get('expiration_date', default=None)

    hash_value = xxh64(str_key).intdigest()
    healthy_nodes = client.get_healthy_nodes()
    v_node_idx = hash_value % N_VIRTUAL_NODES

    target_node = healthy_nodes[v_node_idx % len(healthy_nodes)]
    alt_target_node = healthy_nodes[(v_node_idx + 1) % len(healthy_nodes)]

    error = None
    try:
        client.put(target_node, str_key, data, expiration_date)
    except e:
        error = e

    client.put(alt_target_node, str_key, data, expiration_date)
    return "Success"
    if error is not None:
        raise error 

@app.route("/get")
def get_from_cache():
    str_key = request.args.get('str_key', default="")

    hash_value = xxh64(str_key).intdigest()
    healthy_nodes = client.get_healthy_nodes()
    v_node_idx = hash_value % N_VIRTUAL_NODES

    target_node = healthy_nodes[v_node_idx % len(healthy_nodes)]
    alt_target_node = healthy_nodes[(v_node_idx + 1) % len(healthy_nodes)]

    error = None
    try:
        return client.get(target_node, str_key)
    except e:
        error = e

    return client.get(alt_target_node, str_key)
    if error is not None:
        raise error

@app.route("/cache")
def get_cache():
    res = []
    healthy_nodes = client.get_healthy_nodes()
    for node in healthy_nodes:
        res.append(client.get_cache(node))
    
    print(res)
    return json.dumps(res)

@app.route("/health-check")
def health_check():
    return Response(status=200)

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=80, debug = True)
