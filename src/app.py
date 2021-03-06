import json
from flask import Flask, Response, request
from xxhash import xxh64

from client import EC2_Client
from utils import (
    get_my_node_idx,
    get_instance_id,
    filter_target_from_id,
    update_buckets as update_my_buckets
)

app = Flask(__name__)
client = EC2_Client()

N_VIRTUAL_NODES = 1024

buckets = {
    'mapping': [
        {
            'node': -1,
            'alt_node': -1,
        }
    ] * N_VIRTUAL_NODES,
    'n_healthy_nodes': 0
}


@app.route("/put")
def put_to_cache():
    str_key = request.args.get('str_key', default="")
    data = request.args.get('data', default=None)
    expiration_date = request.args.get('expiration_date', default=None)

    hash_value = xxh64(str_key).intdigest()
    bucket_idx = hash_value % N_VIRTUAL_NODES
    healthy_nodes = client.get_healthy_nodes()

    client.update_nodes(buckets, N_VIRTUAL_NODES)

    target_node = filter_target_from_id(
        healthy_nodes, buckets['mapping'][bucket_idx]['node']
    )
    alt_target_node = filter_target_from_id(
        healthy_nodes, buckets['mapping'][bucket_idx]['alt_node']
    )

    error, success = None, None
    try:
        success = client.put(
            target_node, bucket_idx, str_key, data, expiration_date
        )
    except Exception as e:
        error = e

    try:
        success = client.put(
            alt_target_node, bucket_idx, str_key, data, expiration_date
        )
    except Exception as e:
        error = e

    if error and not success:
        return "Unable to put value", 400

    return "Success"


@app.route("/get")
def get_from_cache():
    str_key = request.args.get('str_key', default="")

    hash_value = xxh64(str_key).intdigest()
    bucket_idx = hash_value % N_VIRTUAL_NODES
    healthy_nodes = client.get_healthy_nodes()

    client.update_nodes(buckets, N_VIRTUAL_NODES)

    target_node = filter_target_from_id(
        healthy_nodes, buckets['mapping'][bucket_idx]['node']
    )
    alt_target_node = filter_target_from_id(
        healthy_nodes, buckets['mapping'][bucket_idx]['alt_node']
    )

    value = None, None
    try:
        value = client.get(target_node, bucket_idx, str_key)
    except Exception:
        try:
            value = client.get(alt_target_node, bucket_idx, str_key)
        except Exception:
            return "Unable to get value", 400

    return value


@app.route("/cache")
def get_cache():
    res = []

    healthy_nodes = client.get_healthy_nodes()

    client.update_nodes(buckets, N_VIRTUAL_NODES)

    for node in healthy_nodes:
        res.append(client.get_cache(node))

    return json.dumps(res, indent=2)


@app.route("/update_buckets", methods=["POST"])
def update_buckets():
    global buckets

    healthy_nodes = client.get_healthy_nodes()
    n_healthy_nodes = len(healthy_nodes)
    new_buckets = json.loads(request.data).get(
        'buckets',
        update_my_buckets(
            buckets, n_healthy_nodes, N_VIRTUAL_NODES, healthy_nodes
        )
    )

    if n_healthy_nodes > 2:
        my_cache = client.get_cache(
            filter_target_from_id(healthy_nodes, get_instance_id())
        )
        for bucket_idx, bucket in enumerate(new_buckets['mapping']):
            is_bucket_in_cache = bool(
                my_cache['cache'].get(str(bucket_idx), None)
            )
            if is_bucket_in_cache:
                my_id = get_instance_id()

                current_node_id = bucket['node']
                current_node_alt_id = bucket['alt_node']

                is_not_in_current = \
                    current_node_id != my_id and current_node_alt_id != my_id

                if is_not_in_current:
                    node_ip = client.get_node_ip(current_node_id)
                    alt_node_ip = client.get_node_ip(current_node_alt_id)

                    try:
                        client.delete_and_send(
                            bucket_idx, node_ip, alt_node_ip
                        )
                    except Exception:
                        print(
                            f"Unable to delete and copy: bucket {bucket_idx}"
                        )

                elif current_node_id == my_id:
                    try:
                        client.send_bucket(
                            current_node_alt_id, bucket_idx
                        )
                    except Exception:
                        print(
                            f"Unable to copy: bucket {bucket_idx}"
                        )

                elif current_node_alt_id == my_id:
                    try:
                        client.send_bucket(
                            current_node_id, bucket_idx
                        )
                    except Exception:
                        print(
                            f"Unable to copy: bucket {bucket_idx}"
                        )

    if n_healthy_nodes == 2:
        source_idx = get_my_node_idx(healthy_nodes)
        target_idx = (source_idx + 1) % n_healthy_nodes

        try:
            client.copy(healthy_nodes[source_idx], healthy_nodes[target_idx])
        except Exception:
            print(f"Unable to copy cache from: {source_idx} to {target_idx}")

    buckets = new_buckets

    return "Success"


@app.route("/health-check")
def health_check():
    return Response(status=200)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
