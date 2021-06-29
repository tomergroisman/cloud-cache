from flask import Flask, request
import json  

from cache import Node_Cache
from utils import get_instance_id

app = Flask(__name__)
cache = Node_Cache()
instance_id = get_instance_id()

@app.route("/put", methods=['POST'])
def put_to_cache():
    n_bucket = request.args.get('n_bucket', -1)
    str_key = request.args.get('str_key', default="")
    data = request.args.get('data', default=None)
    expiration_date = request.args.get('expiration_date', default=None)

    cache.put(n_bucket, str_key, data, expiration_date)
    return f"Success, instance_id: {instance_id}\n"

@app.route("/put-bucket", methods=['POST'])
def put_bucket_to_cache():
    n_bucket = request.data.get('n_bucket', -1)
    str_key = request.data.get('bucket_data', {})

    cache.put_bucket(n_bucket, bucket_data)
    return f"Success, instance_id: {instance_id}\n"

@app.route("/get", methods=['GET'])
def get_from_cache():
  n_bucket = request.args.get('n_bucket', -1)
  str_key = request.args.get('str_key', default="")

  data = cache.get(n_bucket, str_key)
  return f"{data}\n"

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
  n_bucket = request.args.get('n_bucket', -1)
  bucket_data = cache.delete()

  url = f"http://{my_ip}:{VPC_PORT}/put-bucket"
  res = requests.post(url, data={
    "n_bucket": n_bucket,
    "bucket_data": bucket_data
  })

  return "Success"
  

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=8081, debug = True)
