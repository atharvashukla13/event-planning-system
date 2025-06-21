#!/usr/bin/env python3
import subprocess
import time
import sys
import os
from colorama import init, Fore, Style

init()

def print_banner():
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"     EVENT PLANNING SYSTEM - DEMO RUNNER")
    print(f"{'='*60}{Style.RESET_ALL}\n")

def check_rabbitmq():
    print(f"{Fore.YELLOW}Checking RabbitMQ...{Style.RESET_ALL}")
    try:
        import pika
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        connection.close()
        print(f"{Fore.GREEN}✓ RabbitMQ is running!{Style.RESET_ALL}\n")
        return True
    except:
        print(f"{Fore.RED}✗ RabbitMQ is not running!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please start RabbitMQ first:")
        print(f"  docker-compose up -d{Style.RESET_ALL}\n")
        return False

def run_demo():
    print_banner()
    
    if not check_rabbitmq():
        return
    
    processes = []
    
    try:
        # Start Coordinator
        print(f"{Fore.CYAN}Starting Coordinator...{Style.RESET_ALL}")
        coordinator = subprocess.Popen([sys.executable, 'coordinator/coordinator.py'])
        processes.append(coordinator)
        time.sleep(2)
        
        # Start Guests
        guests = [
            ('guest_alice', 'Alice'),
            ('guest_bob', 'Bob'),
            ('guest_charlie', 'Charlie'),
            ('guest_diana', 'Diana'),
            ('guest_eve', 'Eve')
        ]
        
        print(f"{Fore.CYAN}Starting Guests...{Style.RESET_ALL}")
        for guest_id, guest_name in guests:
            guest = subprocess.Popen([sys.executable, 'guest/guest.py', guest_id, guest_name])
            processes.append(guest)
            print(f"  ✓ Started {guest_name}")
            time.sleep(0.5)
        
        # Start Web Dashboard
        print(f"\n{Fore.CYAN}Starting Web Dashboard...{Style.RESET_ALL}")
        dashboard = subprocess.Popen([sys.executable, 'web_dashboard/app_integrated.py'])
        processes.append(dashboard)
        time.sleep(2)
        
        print(f"\n{Fore.GREEN}✓ All services started!{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Dashboard available at: http://localhost:5000{Style.RESET_ALL}")
        
        # Start Host
        print(f"\n{Fore.CYAN}Starting Host Application...{Style.RESET_ALL}")
        time.sleep(2)
        
        # Run host in the main thread so user can interact
        os.system(f'{sys.executable} host/host.py "Demo Host"')
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down demo...{Style.RESET_ALL}")
    finally:
        # Clean up all processes
        for process in processes:
            process.terminate()
        print(f"{Fore.GREEN}Demo stopped.{Style.RESET_ALL}")

if __name__ == "__main__":
    run_demo()