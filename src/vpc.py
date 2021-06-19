from flask import Flask, request
import json  

from cache import Node_Cache
from utils import get_instance_id

app = Flask(__name__)
cache = Node_Cache()
instance_id = get_instance_id()

@app.route("/put", methods=['POST'])
def put_to_cache():
    str_key = request.args.get('str_key', default="")
    data = request.args.get('data', default=None)
    expiration_date = request.args.get('expiration_date', default=None)

    cache.put(str_key, data, expiration_date)
    return f"Success, instance_id: {instance_id}\n"

@app.route("/get", methods=['GET'])
def get_from_cache():
  str_key = request.args.get('str_key', default="")

  data = cache.get(str_key)
  return f"{data}\n"

@app.route("/cache", methods=['GET'])
def get_cache():
  data = cache.get_cache()
  res = {
    "instance_id": instance_id,
    "cache": data
  }
  return json.dumps(res, indent=2)

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=8080, debug = True)
