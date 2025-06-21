import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from config.settings import Config
from common.models import EventInvitation, GuestResponse, EventSummary
from common.pubsub_client import RabbitMQClient
import json
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store events and responses
events_data = {}
responses_data = {}

# RabbitMQ client for dashboard
dashboard_client = None

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

def process_event_message(message):
    """Process incoming event invitations"""
    try:
        event = EventInvitation.from_json(message.decode('utf-8'))
        event_dict = {
            'event_id': event.event_id,
            'host_name': event.host_name,
            'event_name': event.event_name,
            'date_time': event.date_time,
            'location': event.location,
            'description': event.description
        }
        events_data[event.event_id] = event_dict
        
        # Broadcast to all connected clients
        socketio.emit('new_event', event_dict)
        print(f"Dashboard: New event received - {event.event_name}")
    except Exception as e:
        print(f"Error processing event: {e}")

def process_response_message(message):
    """Process incoming guest responses"""
    try:
        response = GuestResponse.from_json(message.decode('utf-8'))
        response_dict = {
            'guest_id': response.guest_id,
            'guest_name': response.guest_name,
            'event_id': response.event_id,
            'response': response.response,
            'message': response.message,
            'timestamp': response.timestamp
        }
        
        # Store response
        if response.event_id not in responses_data:
            responses_data[response.event_id] = []
        responses_data[response.event_id].append(response_dict)
        
        # Broadcast to all connected clients
        socketio.emit('new_response', response_dict)
        print(f"Dashboard: Response received from {response.guest_name} - {response.response}")
    except Exception as e:
        print(f"Error processing response: {e}")

def listen_to_events():
    """Background thread to listen to RabbitMQ events"""
    try:
        client = RabbitMQClient()
        
        # Declare exchanges
        client.declare_exchange(Config.INVITATION_EXCHANGE, 'direct')
        client.declare_exchange(Config.RESPONSE_EXCHANGE, 'direct')
        
        # Create dashboard queues
        event_queue = client.declare_queue('dashboard.events')
        response_queue = client.declare_queue('dashboard.responses')
        
        # Bind to all events (using fanout pattern for dashboard)
        # For invitations, we'll bind to coordinator routing key
        client.bind_queue(event_queue, Config.INVITATION_EXCHANGE, 'coordinator')
        
        # For responses, we'll also bind to coordinator routing key
        client.bind_queue(response_queue, Config.RESPONSE_EXCHANGE, 'coordinator')
        
                # Start consuming in separate threads
        def consume_events():
            client.consume(event_queue, process_event_message)
        
        def consume_responses():
            client2 = RabbitMQClient()  # Need separate connection for parallel consuming
            client2.consume(response_queue, process_response_message)
        
        # Start consumers
        event_thread = threading.Thread(target=consume_events, daemon=True)
        response_thread = threading.Thread(target=consume_responses, daemon=True)
        
        event_thread.start()
        response_thread.start()
        
        print("Dashboard listening to RabbitMQ events...")
        
    except Exception as e:
        print(f"Error setting up RabbitMQ listener: {e}")

def run_server():
    # Start RabbitMQ listener in background
    listener_thread = threading.Thread(target=listen_to_events, daemon=True)
    listener_thread.start()
    time.sleep(2)  # Give it time to connect
    
    # Start Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=Config.FLASK_PORT, debug=False)

if __name__ == '__main__':
    run_server()