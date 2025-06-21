import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.models import EventInvitation, GuestResponse, EventSummary
from common.pubsub_client import RabbitMQClient
from config.settings import Config
import logging
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Coordinator:
    def __init__(self):
        self.client = RabbitMQClient()
        self.setup_queues()
        self.active_events = {}
        self.guest_responses = defaultdict(list)
        self.registered_guests = ['guest_alice', 'guest_bob', 'guest_charlie', 'guest_diana', 'guest_eve']
        self.timers = {}
    
    def setup_queues(self):
        # Declare all exchanges
        self.client.declare_exchange(Config.INVITATION_EXCHANGE, 'direct')
        self.client.declare_exchange(Config.RESPONSE_EXCHANGE, 'direct')
        self.client.declare_exchange(Config.SUMMARY_EXCHANGE, 'direct')
        
        # Coordinator's inbox queue
        self.coordinator_queue = self.client.declare_queue(Config.COORDINATOR_QUEUE)
        
        # Bind to receive invitations from hosts
        self.client.bind_queue(self.coordinator_queue, Config.INVITATION_EXCHANGE, 'coordinator')
        
        # Bind to receive responses from guests
        self.client.bind_queue(self.coordinator_queue, Config.RESPONSE_EXCHANGE, 'coordinator')
    
    def handle_invitation(self, invitation: EventInvitation):
        logger.info(f"Received invitation for event: {invitation.event_name} (ID: {invitation.event_id})")
        
        # Store event details
        self.active_events[invitation.event_id] = invitation
        
        # Forward to all registered guests
        for guest_id in self.registered_guests:
            logger.info(f"Forwarding invitation to {guest_id}")
            self.client.publish(
                Config.INVITATION_EXCHANGE,
                guest_id,
                invitation.to_json()
            )
        
        # Set timer for response collection
        timer = threading.Timer(Config.RESPONSE_TIMEOUT, self.compile_and_send_summary, args=[invitation.event_id])
        timer.start()
        self.timers[invitation.event_id] = timer
        
        logger.info(f"Timer set for {Config.RESPONSE_TIMEOUT} seconds for event {invitation.event_id}")
    
    def handle_guest_response(self, response: GuestResponse):
        logger.info(f"Received response from {response.guest_name}: {response.response}")
        
        # Store response
        self.guest_responses[response.event_id].append(response)
    
    def compile_and_send_summary(self, event_id: str):
        logger.info(f"Compiling summary for event {event_id}")
        
        if event_id not in self.active_events:
            logger.error(f"Event {event_id} not found")
            return
        
        event = self.active_events[event_id]
        responses = self.guest_responses[event_id]
        
        # Create summary
        summary = EventSummary(
            event_id=event_id,
            event_name=event.event_name,
            total_invited=len(self.registered_guests),
            responses=[{
                'guest_id': r.guest_id,
                'guest_name': r.guest_name,
                'response': r.response,
                'message': r.message,
                'timestamp': r.timestamp
            } for r in responses]
        )
        
        # Count responses
        for response in responses:
            if response.response == "Yes":
                summary.attending_count += 1
            elif response.response == "No":
                summary.not_attending_count += 1
            elif response.response == "Maybe":
                summary.maybe_count += 1
        
        summary.no_response_count = summary.total_invited - len(responses)
        
        # Send summary back to host
        logger.info(f"Sending summary to host: {event.host_name}")
        self.client.publish(
            Config.SUMMARY_EXCHANGE,
            event.host_name,
            summary.to_json()
        )
        
        # Clean up
        del self.active_events[event_id]
        del self.guest_responses[event_id]
        if event_id in self.timers:
            del self.timers[event_id]
    
    def process_message(self, message):
        try:
            # Try to parse as invitation first
            data = message.decode('utf-8')
            if 'event_name' in data:
                invitation = EventInvitation.from_json(data)
                self.handle_invitation(invitation)
            elif 'guest_id' in data:
                response = GuestResponse.from_json(data)
                self.handle_guest_response(response)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def run(self):
        logger.info("Coordinator started and listening for messages...")
        try:
            self.client.consume(self.coordinator_queue, self.process_message)
        except KeyboardInterrupt:
            logger.info("Coordinator shutting down...")
        finally:
            self.client.close()

if __name__ == "__main__":
    coordinator = Coordinator()
    coordinator.run()