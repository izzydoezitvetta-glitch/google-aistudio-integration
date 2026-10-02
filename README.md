# google-aistudio-integration
Google AI Studio integration with GitHub for AI-powered applications

# AI Studio Hub

A production-ready, security-focused full-stack app for Google AI Studio / Gemini.

## Stack
- Backend: Python + FastAPI
- Frontend: React + Vite
- AI: Google Generative AI / Gemini
- Security: JWT, bcrypt, rate limiting, security headers

## Features
- Secure API authentication
- Google AI Studio integration
- Chat endpoint with prompt templates
- Summarization endpoint
- Frontend dashboard
- CI pipeline configuration

## Quick start

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```

## Required environment values
- GOOGLE_API_KEY
- JWT_SECRET
- SECRET_KEY
- ENCRYPTION_KEY

Never commit .env files to GitHub.
