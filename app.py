from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return flask.Response(status=200)

@app.route('/health-check')
def health_check():
    return 'Hello World!'