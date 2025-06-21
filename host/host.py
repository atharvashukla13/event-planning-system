import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.models import EventInvitation, EventSummary
from common.pubsub_client import RabbitMQClient
from config.settings import Config
from colorama import init, Fore, Style
import logging
from datetime import datetime, timedelta
import threading

init()
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class EventHost:
    def __init__(self, host_name="Party Host"):
        self.host_name = host_name
        self.client = RabbitMQClient()
        self.setup_queues()
        self.pending_events = {}
        self.received_summaries = {}
    
    def setup_queues(self):
        # Declare exchanges - use 'direct' to match coordinator
        self.client.declare_exchange(Config.INVITATION_EXCHANGE, 'direct')  # Changed from default 'fanout'
        self.client.declare_exchange(Config.SUMMARY_EXCHANGE, 'direct')     # Changed from default 'fanout'
    
        # Create unique queue for this host
        self.summary_queue = self.client.declare_queue(f'{Config.HOST_QUEUE_PREFIX}.{self.host_name}.summaries')
        self.client.bind_queue(self.summary_queue, Config.SUMMARY_EXCHANGE, self.host_name)
    def create_event(self):
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"       CREATE NEW EVENT")
        print(f"{'='*50}{Style.RESET_ALL}\n")
        
        event = EventInvitation()
        event.host_name = self.host_name
        
        print(f"{Fore.YELLOW}Enter event details:{Style.RESET_ALL}")
        event.event_name = input(f"{Fore.GREEN}Event Name: {Style.RESET_ALL}")
        
        # Get date
        date_str = input(f"{Fore.GREEN}Event Date (YYYY-MM-DD) [Enter for tomorrow]: {Style.RESET_ALL}")
        if not date_str:
            event_date = datetime.now() + timedelta(days=1)
        else:
            event_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        time_str = input(f"{Fore.GREEN}Event Time (HH:MM) [Enter for 19:00]: {Style.RESET_ALL}") or "19:00"
        event_time = datetime.strptime(time_str, "%H:%M").time()
        
        event.date_time = datetime.combine(event_date.date(), event_time).isoformat()
        event.location = input(f"{Fore.GREEN}Location: {Style.RESET_ALL}")
        event.description = input(f"{Fore.GREEN}Description: {Style.RESET_ALL}")
        
        capacity = input(f"{Fore.GREEN}Max Capacity [Enter for unlimited]: {Style.RESET_ALL}")
        if capacity:
            event.max_capacity = int(capacity)
        
        self.pending_events[event.event_id] = event
        return event
    
    def send_invitation(self, event: EventInvitation):
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"       SENDING INVITATION")
        print(f"{'='*50}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Event Details:")
        print(f"  • Name: {event.event_name}")
        print(f"  • Date/Time: {event.date_time}")
        print(f"  • Location: {event.location}")
        print(f"  • Event ID: {event.event_id}{Style.RESET_ALL}")
        
        # Publish to coordinator
        self.client.publish(
            Config.INVITATION_EXCHANGE,
            'coordinator',
            event.to_json()
        )
        
        print(f"\n{Fore.GREEN}✓ Invitation sent successfully!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⏳ Waiting for guest responses...{Style.RESET_ALL}\n")
    
    def process_summary(self, message):
        try:
            summary = EventSummary.from_json(message.decode('utf-8'))
            self.received_summaries[summary.event_id] = summary
            
            print(f"\n{Fore.YELLOW}{'='*50}")
            print(f"       EVENT SUMMARY RECEIVED")
            print(f"{'='*50}{Style.RESET_ALL}\n")
            
            print(f"{Fore.CYAN}Event: {summary.event_name}{Style.RESET_ALL}")
            print(f"Total Invited: {summary.total_invited}")
            
            print(f"\n{Fore.WHITE}Response Summary:{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}✓ Attending: {summary.attending_count}{Style.RESET_ALL}")
            print(f"  {Fore.RED}✗ Not Attending: {summary.not_attending_count}{Style.RESET_ALL}")
            print(f"  {Fore.YELLOW}? Maybe: {summary.maybe_count}{Style.RESET_ALL}")
            print(f"  {Fore.BLUE}⏳ No Response: {summary.no_response_count}{Style.RESET_ALL}")
            
            if summary.responses:
                print(f"\n{Fore.CYAN}Guest List:{Style.RESET_ALL}")
                print(f"{'Name':<20} {'Response':<15} {'Message':<30}")
                print("-" * 65)
                
                for response in summary.responses:
                    color = Fore.GREEN if response['response'] == 'Yes' else Fore.RED if response['response'] == 'No' else Fore.YELLOW
                    message = response.get('message', '')[:30]
                    print(f"{response['guest_name']:<20} {color}{response['response']:<15}{Style.RESET_ALL} {message}")
            
            print(f"\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}\n")
            
        except Exception as e:
            logger.error(f"Error processing summary: {e}")
    
    def listen_for_summaries(self):
        # This runs in a separate thread
        self.client.consume(self.summary_queue, self.process_summary)
    
    def run(self):
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"       EVENT HOST SYSTEM")
        print(f"       Host: {self.host_name}")
        print(f"{'='*50}{Style.RESET_ALL}\n")
        
        # Start listening for summaries in background
        listener_thread = threading.Thread(target=self.listen_for_summaries, daemon=True)
        listener_thread.start()
        
        while True:
            print(f"\n{Fore.CYAN}Options:")
            print(f"1. Create and send invitation")
            print(f"2. View received summaries")
            print(f"3. Exit{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}")
            
            if choice == '1':
                event = self.create_event()
                self.send_invitation(event)
            elif choice == '2':
                if self.received_summaries:
                    print(f"\n{Fore.CYAN}Received Summaries:{Style.RESET_ALL}")
                    for event_id, summary in self.received_summaries.items():
                        print(f"- {summary.event_name} (ID: {event_id[:8]}...)")
                else:
                    print(f"{Fore.YELLOW}No summaries received yet.{Style.RESET_ALL}")
            elif choice == '3':
                print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                break

if __name__ == "__main__":
    import sys
    host_name = sys.argv[1] if len(sys.argv) > 1 else "Default Host"
    host = EventHost(host_name)
    try:
        host.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down...{Style.RESET_ALL}")
    finally:
        host.client.close()