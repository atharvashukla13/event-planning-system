import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # RabbitMQ settings
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    
    # Exchange names
    INVITATION_EXCHANGE = 'event.invitations'
    RESPONSE_EXCHANGE = 'guest.responses'
    SUMMARY_EXCHANGE = 'event.summaries'
    
    # Queue names
    COORDINATOR_QUEUE = 'coordinator.inbox'
    HOST_QUEUE_PREFIX = 'host'
    GUEST_QUEUE_PREFIX = 'guest'
    
    # Timeouts
    RESPONSE_TIMEOUT = int(os.getenv('RESPONSE_TIMEOUT', 30))
    
    # Flask settings
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))