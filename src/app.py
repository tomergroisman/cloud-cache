import json
from flask import Flask, Response, request
from xxhash import xxh64

from client import EC2_Client
from utils import healthy_nodes_change, update_nodes, get_my_node_idx

app = Flask(__name__)
client = EC2_Client()

N_VIRTUAL_NODES = 1024

buckets = {
    'mapping': [
        {
        'node': -1,
        'alt_node': -1
        }
    ] * N_VIRTUAL_NODES,
    'n_healthy_nodes': 0
}

@app.route("/put")
def put_to_cache():
    str_key = request.args.get('str_key', default="")
    data = request.args.get('data', default=None)
    expiration_date = request.args.get('expiration_date', default=None)
    
    update_nodes(client, buckets)

    hash_value = xxh64(str_key).intdigest()
    bucket_idx = hash_value % N_VIRTUAL_NODES
    healthy_nodes = client.get_healthy_nodes()
    n_healthy_nodes = len(healthy_nodes)

    target_node = healthy_nodes[buckets['mapping'][bucket_idx]['node']]
    alt_target_node = healthy_nodes[(buckets['mapping'][bucket_idx]['node'] + 1) % n_healthy_nodes]

    error = None
    try:
        client.put(target_node, bucket_idx, str_key, data, expiration_date)
    except e:
        error = e

    client.put(alt_target_node, bucket_idx, str_key, data, expiration_date)
    return "Success"
    if error is not None:
        raise error 

@app.route("/get")
def get_from_cache():
    str_key = request.args.get('str_key', default="")

    hash_value = xxh64(str_key).intdigest()
    bucket_idx = hash_value % N_VIRTUAL_NODES
    healthy_nodes = client.get_healthy_nodes()
    n_healthy_nodes = len(healthy_nodes)

    target_node = healthy_nodes[bucket_idx % n_healthy_nodes]
    alt_target_node = healthy_nodes[(bucket_idx + 1) % n_healthy_nodes]

    update_nodes(client, buckets)

    error, value = None, None
    try:
        value = client.get(target_node, bucket_idx, str_key)
    except Exception as e:
        error = e

    if not value:
        value = client.get(alt_target_node, bucket_idx, str_key)

    if error is not None:
        raise error

    return value

@app.route("/cache")
def get_cache():
    res = []

    healthy_nodes = client.get_healthy_nodes()

    for node in healthy_nodes:
        res.append(client.get_cache(node))
    
    return json.dumps(res, indent=2)

@app.route("/update_buckets", methods=["POST"])
def update_buckets():
    healthy_nodes = client.get_healthy_nodes()
    n_healthy_nodes = len(healthy_nodes)

    if n_healthy_nodes == 1:
        return "Success"

    if n_healthy_nodes == 2:
        source_idx = get_my_node_idx(healthy_nodes)
        target_idx = (source_idx + 1) % n_healthy_nodes
        client.copy(healthy_nodes[source_idx], healthy_nodes[target_idx])

        return "Success"

    for bucket_idx, bucket in enumerate(buckets['mapping']):
        prev_node = bucket['node']
        prev_node_alt = bucket['node']
        buckets['mapping'][bucket_idx]['node'] = N_VIRTUAL_NODES % n_healthy_nodes
        buckets['mapping'][bucket_idx]['alt_node'] = (N_VIRTUAL_NODES + 1) % n_healthy_nodes

        my_idx = get_my_node_idx(healthy_nodes)

        is_in_prev = prev_node == my_idx or prev_node_alt == my_idx
        is_in_current = bucket['node'] != my_idx or bucket['alt_node']
    
        if is_in_prev and is_in_current:
            client.delete_and_send(bucket_idx)

    return "Success"

@app.route("/health-check")
def health_check():
    return Response(status=200)

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=8080, debug = True)
