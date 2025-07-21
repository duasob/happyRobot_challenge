# Happy Robot Challenge

This is a Flask-based API and dashboard for managing and booking carrier loads, hosted on [Vercel](https://vercel.com/).

## 🌐 Live Web App

**Dashboard & API:**  
https://happy-robot-challenge-jweajqeqa-brunos-projects-7e1456d0.vercel.app

- `/dashboard` — Modern dashboard UI for viewing and booking loads
- `/carriers/api/carriers` — API endpoint for all carriers (requires API key)
- `/carriers/api/bookings` — API endpoint for all bookings (requires API key)
- `/webhook/` — Webhook endpoint for booking loads (requires API key)

All the endpoints are protected via an API Key.

To acess the dashboard:
```
https://happy-robot-challenge-jweajqeqa-brunos-projects-7e1456d0.vercel.app/dashboard?api_key={key}
```

## Local Development

Create or paste your `.env` file at the source of the repo.

1. **Clone the repo:**
   ```bash
   git clone <this-repo-url>
   cd happyRobot_challenge
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
3. **Run Flask app:**
   ```bash
   export FLASK_APP=api/index.py
   flask run
   ```
   The app will be available at http://localhost:5000

## 🐳 Docker

Build and run with Docker:
```bash
docker build -t happyrobot .
docker run -p 5000:5000 happyrobot
```

##  Deploying to Vercel
- The app and DockerFile are already set up for Vercel deployment (see `Dockerfile` and `api/index.py`), but you will need to enter your (free) accout info
- You can use the Vercel CLI for custom deployments.

## 🔑 Authentication
- All API endpoints require an API key via the `X-API-KEY` header or `api_key` query parameter.

## 📬 Example Webhook POST
```bash
curl -X POST https://happy-robot-challenge-jweajqeqa-brunos-projects-7e1456d0.vercel.app/webhook/ \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: UBNfljhgZwVGTIIXMsgH27EQHz4WULkX29k3dnsN8r0" \
  -d '{
    "mc_num": "102743",
    "chosen_id": "LOAD001",
    "final_rate": "1875",
    "initial_rate": "1800",
    "transcript": "[ ... JSON ... ]",
    "sentiment": "Positive",
    "duration": "120"
  }'
```

---

