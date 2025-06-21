import pika
import os
from typing import Callable
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self, host='localhost', port=5672):
        self.host = os.getenv('RABBITMQ_HOST', host)
        self.port = int(os.getenv('RABBITMQ_PORT', port))
        self.connection = None
        self.channel = None
        self.connect()
    
    def connect(self):
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.host, 
                        port=self.port,
                        heartbeat=600,
                        blocked_connection_timeout=300
                    )
                )
                self.channel = self.connection.channel()
                logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
                return
            except Exception as e:
                retry_count += 1
                logger.warning(f"Failed to connect to RabbitMQ (attempt {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    time.sleep(2)
                else:
                    raise
    
    def declare_exchange(self, exchange_name, exchange_type='fanout'):
        self.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)
    
    def declare_queue(self, queue_name, durable=True):
        result = self.channel.queue_declare(queue=queue_name, durable=durable)
        return result.method.queue
    
    def bind_queue(self, queue_name, exchange_name, routing_key=''):
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
    
    def publish(self, exchange, routing_key, message):
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        logger.info(f"Published message to {exchange}/{routing_key}")
    
    def consume(self, queue_name, callback: Callable):
        def wrapper(ch, method, properties, body):
            try:
                callback(body)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=queue_name, on_message_callback=wrapper)
        logger.info(f"Starting to consume from {queue_name}")
        self.channel.start_consuming()
    
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()