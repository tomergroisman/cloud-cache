from flask import Flask, Response
app = Flask(__name__)

@app.route('/put')
def put_to_cache():
    return "in put"

@app.route('/get')
def get_from_cache():
    return "in get"

@app.route('/health-check')
def health_check():
    return Response(status=200)