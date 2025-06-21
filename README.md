# 🎉 Event Planning System

A distributed event planning system using Pub/Sub architecture with Python and RabbitMQ.

## 📋 Features

- **Event Host**: Create and send event invitations
- **Coordinator**: Central hub that manages event flow
- **Event Guests**: Receive invitations and respond with attendance decisions
- **Web Dashboard**: Real-time monitoring of events and responses
- **Personality-based Responses**: Guests have different personalities affecting their decisions

## 🏗️ Architecture

┌─────────┐ ┌─────────────┐ ┌─────────┐
│ Host │ ──1──> │ Coordinator │ ──2──> │ Guests │
└─────────┘ │ (Hub) │ └─────────┘
↑ │ │ │
└──────4───────┤ │<─────3───────┘
└─────────────┘

1. Host publishes invitation to Coordinator
2. Coordinator forwards invitation to all registered Guests
3. Guests send responses back to Coordinator
4. Coordinator compiles summary and sends to Host

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd event-planning-system
   ```
