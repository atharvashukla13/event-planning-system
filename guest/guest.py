import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.models import EventInvitation, GuestResponse
from common.pubsub_client import RabbitMQClient
from config.settings import Config
from colorama import init, Fore, Style
import logging
import random
import time

init()
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class EventGuest:
    def __init__(self, guest_id, guest_name):
        self.guest_id = guest_id
        self.guest_name = guest_name
        self.client = RabbitMQClient()
        self.setup_queues()
        self.personality = self.generate_personality()
    
    def setup_queues(self):
        # Declare exchanges
        self.client.declare_exchange(Config.INVITATION_EXCHANGE, 'direct')
        self.client.declare_exchange(Config.RESPONSE_EXCHANGE, 'direct')
        
        # Create unique queue for this guest
        self.invitation_queue = self.client.declare_queue(f'{Config.GUEST_QUEUE_PREFIX}.{self.guest_id}.invitations')
        self.client.bind_queue(self.invitation_queue, Config.INVITATION_EXCHANGE, self.guest_id)
    
    def generate_personality(self):
        # Create a personality for the guest
        personalities = [
            {"type": "enthusiastic", "yes_probability": 0.8, "maybe_probability": 0.15},
            {"type": "busy", "yes_probability": 0.3, "maybe_probability": 0.4},
            {"type": "social", "yes_probability": 0.7, "maybe_probability": 0.2},
            {"type": "introverted", "yes_probability": 0.2, "maybe_probability": 0.3},
            {"type": "spontaneous", "yes_probability": 0.6, "maybe_probability": 0.3}
        ]
        return random.choice(personalities)
    
    def decide_attendance(self, invitation: EventInvitation):
        # Simulate decision making
        print(f"\n{Fore.YELLOW}{'='*50}")
        print(f"       NEW INVITATION RECEIVED!")
        print(f"{'='*50}{Style.RESET_ALL}\n")
        
        print(f"{Fore.CYAN}From: {invitation.host_name}")
        print(f"Event: {invitation.event_name}")
        print(f"When: {invitation.date_time}")
        print(f"Where: {invitation.location}")
        print(f"Details: {invitation.description}{Style.RESET_ALL}")
        
        # Thinking delay
        thinking_time = random.uniform(2, 5)
        print(f"\n{Fore.YELLOW}🤔 {self.guest_name} is thinking... (Personality: {self.personality['type']}){Style.RESET_ALL}")
        time.sleep(thinking_time)
        
        # Make decision based on personality
        rand = random.random()
        if rand < self.personality['yes_probability']:
            response = "Yes"
            messages = [
                "Can't wait! 🎉",
                "Absolutely! Count me in!",
                "Sounds amazing! I'll be there!",
                "Looking forward to it!",
                "Wouldn't miss it for the world!"
            ]
        elif rand < self.personality['yes_probability'] + self.personality['maybe_probability']:
            response = "Maybe"
            messages = [
                "I'll try to make it!",
                "Sounds fun, but I need to check my schedule",
                "Put me down as a maybe",
                "I'll let you know closer to the date",
                "Depends on work, but I'll try!"
            ]
        else:
            response = "No"
            messages = [
                "Sorry, can't make it 😢",
                "Already have plans that day",
                "Unfortunately I'll be out of town",
                "Can't attend, but have fun!",
                "Sorry, won't be able to join"
            ]
        
        message = random.choice(messages)
        
        # Color code the decision
        if response == "Yes":
            color = Fore.GREEN
        elif response == "Maybe":
            color = Fore.YELLOW
        else:
            color = Fore.RED
        
        print(f"\n{color}Decision: {response}{Style.RESET_ALL}")
        print(f"Message: {message}")
        
        return response, message
    
    def send_response(self, invitation: EventInvitation, decision: str, message: str):
        response = GuestResponse(
            guest_id=self.guest_id,
            guest_name=self.guest_name,
            event_id=invitation.event_id,
            response=decision,
            message=message
        )
        
        # Send to coordinator
        self.client.publish(
            Config.RESPONSE_EXCHANGE,
            'coordinator',
            response.to_json()
        )
        
        print(f"\n{Fore.GREEN}✓ Response sent to coordinator!{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'='*50}{Style.RESET_ALL}\n")
    
    def process_invitation(self, message):
        try:
            invitation = EventInvitation.from_json(message.decode('utf-8'))
            decision, message_text = self.decide_attendance(invitation)
            self.send_response(invitation, decision, message_text)
        except Exception as e:
            logger.error(f"Error processing invitation: {e}")
    
    def run(self):
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"       GUEST: {self.guest_name}")
        print(f"       ID: {self.guest_id}")
        print(f"       Personality: {self.personality['type']}")
        print(f"{'='*50}{Style.RESET_ALL}\n")
        
        print(f"{Fore.CYAN}Waiting for invitations...{Style.RESET_ALL}\n")
        
        try:
            self.client.consume(self.invitation_queue, self.process_invitation)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}{self.guest_name} is signing off...{Style.RESET_ALL}")
        finally:
            self.client.close()

if __name__ == "__main__":
    # Guest ID and name can be passed as arguments or use defaults
    if len(sys.argv) > 2:
        guest_id = sys.argv[1]
        guest_name = sys.argv[2]
    else:
        guest_id = "guest_default"
        guest_name = "Default Guest"
    
    guest = EventGuest(guest_id, guest_name)
    guest.run()