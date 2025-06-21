# 📅 Event Planning System – Pub/Sub Architecture in Python

This is a modular event invitation system simulating real-world asynchronous communication using the **Publish-Subscribe** model. The project showcases a distributed architecture with decoupled services: `Host`, `Coordinator`, and `Guest`, using **Redis Pub/Sub**. A lightweight web dashboard is also included.

---

## 🚦 System Flow

1. **Host** publishes an event invitation.
2. **Coordinator** listens for invitations, forwards to registered guests.
3. **Guests** decide whether to attend and respond.
4. **Coordinator** collects all guest responses and sends a final summary.
5. **Host** receives and displays the summary.

---

## 📁 Project Structure

event-planning-system/
├── common/ # Shared utilities (models, Redis client)
│ ├── models.py
│ └── pubsub_client.py
├── config/ # App settings and environment configs
│ └── settings.py
├── coordinator/ # Logic to orchestrate guests & responses
│ └── coordinator.py
├── guest/ # Guest logic (decision & response)
│ └── guest.py
├── host/ # Event host logic (invites & summaries)
│ └── host.py
├── tests/ # (Placeholder for future unit tests)
├── web_dashboard/ # Optional web interface (e.g., Streamlit)
│ ├── app.py
│ └── app_integrated.py
├── docker-compose.yml # For running Redis + app containers
├── requirements.txt # Python dependencies
└── README.md # You're here!


## ⚙️ Getting Started

### 🐳 Start Redis (via Docker)

```bash
docker-compose up -d
Or manually:

bash
Copy
Edit
docker run -p 6379:6379 redis
🐍 Install Python Dependencies
Create a virtual environment and install:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
🚀 Running the System
Run each service in its own terminal window or use tabs in VS Code.

🧑‍💼 Host
bash
Copy
Edit
python host/host.py
🧠 Coordinator
bash
Copy
Edit
python coordinator/coordinator.py
🧍 Guests (open multiple terminals or threads)
bash
Copy
Edit
GUEST_NAME=Alice python guest/guest.py
GUEST_NAME=Bob   python guest/guest.py
🌐 Web Dashboard (Optional)

streamlit run web_dashboard/app.py
🧠 Key Features
✅ Modular microservice-style design

✅ Redis Pub/Sub integration

✅ Decoupled services for scalability

✅ Simulated human decision logic for guests

✅ Streamlit dashboard integration

✅ Docker-compatible setup

🧪 Potential Enhancements
If more time was available:

Add retry logic and timeouts for message handling

Deploy to cloud using GCP Pub/Sub or AWS SNS/SQS

Implement persistence with Redis Streams or PostgreSQL

Integrate user login to secure the guest/host flow

Add real-time UI updates via websockets

📽️ Demo Walkthrough
Demo video link: [add your Google Drive or YouTube unlisted link here]
Make sure your video includes:

Terminal views of each component

Guest responses being printed

Final summary at the Host

👨‍💻 Author
Atharva Shukla
GitHub Profile

For any issues or suggestions, feel free to open an issue or PR!

yaml
Copy
Edit

---

Would you like me to generate a `docker-compose.yml` explanation section too? Or do you want help with the video walkthrough script next?
