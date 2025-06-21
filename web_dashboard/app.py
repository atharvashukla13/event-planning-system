import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from config.settings import Config
import json
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store events and responses
events_data = {}
responses_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send current data to new client
    emit('update_data', {
        'events': list(events_data.values()),
        'responses': list(responses_data.values())
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def update_dashboard(event_type, data):
    """Update dashboard with new data"""
    socketio.emit('update_' + event_type, data)

def run_server():
    socketio.run(app, host='0.0.0.0', port=Config.FLASK_PORT, debug=False)

if __name__ == '__main__':
    run_server()