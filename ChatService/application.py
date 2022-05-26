from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS

import logging
import doFlaskLogging

app = Flask(__name__)
socket = SocketIO(app,cors_allowed_origins='*',logger=True)
CORS(app)

@app.route('/')
def index():
    logging.info(f"/ called")
    return "<h1>Health Check is good.  Try doing socket communications instead.</h1>"

@socket.on('connect')
def connect():
    logging.info(f"socket connect called")
    print("[CLIENT CONNECTED]:", request.sid)

@socket.on('disconnect')
def disconn():
    logging.info(f"socket disconnect called")
    print("[CLIENT DISCONNECTED]:", request.sid)

@socket.on('notify')
def notify(user):
    logging.info(f"socket notify called")
    emit('notify', user, broadcast=True, skip_sid=request.sid)

@socket.on('data')
def emitback(data):
    logging.info(f"socket data called")
    emit('returndata', data, broadcast=True)

if __name__ == "__main__":
    doFlaskLogging.set_up_logger()
    socket.run(app,port=8080)
    doFlaskLogging.clean_up_logger()
