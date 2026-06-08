# 🚀 OutreachOS - Your Automated B2B Outreach Machine

Welcome to **OutreachOS**, a production-ready, full-stack application designed to fully automate your B2B outreach efforts. Starting with just a single company domain, OutreachOS handles the entire pipeline: finding similar companies, locating key decision-makers, verifying email addresses, and dispatching personalized outreach emails.

---

## ✨ Capabilities & Integrations

OutreachOS seamlessly orchestrates a powerful pipeline using industry-leading integrations:

1. **🏢 Company Discovery (Ocean.io)**: Identifies companies similar to your target domain.
2. **🎯 Contact Discovery (Prospeo)**: Locates key decision-makers (Founders, CEOs, CTOs, VPs).
3. **📧 Email Resolution (Eazyreach)**: Extracts and verifies work emails from LinkedIn profiles.
4. **✍️ AI-Powered Copywriting (Built-in)**: Generates highly personalized, role-specific email content.
5. **🛡️ Safety Checkpoint (UI)**: Provides a manual review stage before anything is dispatched.
6. **🚀 Delivery Engine (Brevo)**: Handles the final send with built-in retry logic and robust logging.

---

## 🏗️ Architecture & Structure

A clean separation of concerns between a blazing-fast backend and a modern frontend:

```text
outreach-pipeline/
├── backend/                  # Python / FastAPI Backend
│   ├── app/                  # Application Logic
│   │   ├── api/              # API Endpoints (Pipeline, Results, Emails)
│   │   ├── services/         # Integration & Orchestration Logic
│   │   ├── models/           # Data Models (Pydantic)
│   │   ├── config/           # App Configuration & Store
│   │   └── utils/            # Shared Utilities (HTTP, Logging)
│   ├── requirements.txt      # Python Dependencies
│   └── .env.example          # Environment Variables Template
├── frontend/                 # React / Vite Frontend
│   ├── src/
│   │   ├── pages/            # React Pages (Home, Pipeline, Results, Review)
│   │   ├── components/       # Reusable UI Components
│   │   ├── hooks/            # Custom React Hooks
│   │   └── utils/            # Frontend Utilities (API Clients)
│   ├── package.json          # Node Dependencies
│   └── vite.config.js        # Vite Configuration
└── start.sh                  # One-Click Run Script
```

---

## ⚙️ Getting Started

### Prerequisites
- **Python** 3.11 or higher
- **Node.js** 18 or higher
- **npm** or **yarn**

### Quick Start (The Easy Way)
We've included a handy shell script to get both the frontend and backend running simultaneously.

```bash
chmod +x start.sh
./start.sh
```

### Manual Installation

**1. Setup the Backend**
```bash
cd backend
cp .env.example .env  # Add your API keys to the .env file

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**2. Setup the Frontend**
```bash
cd frontend
npm install
npm run dev
# The app will open at http://localhost:3000
```

---

## 🔑 External API Integrations

To unlock the full potential of OutreachOS, you can configure the following API keys in your `.env` file:

- [Ocean.io](https://ocean.io) - For company discovery
- [Prospeo](https://prospeo.io) - For contact discovery
- [Eazyreach](https://eazyreach.io) - For email resolution
- [Brevo](https://brevo.com) - For email delivery (free tier available)

> **💡 Note on Demo Mode:** No API keys? No problem! OutreachOS gracefully falls back to mock data if API keys are not provided, allowing you to experience the full pipeline flow safely.

---

## 📡 Core API Reference

The backend exposes a comprehensive REST API. View the interactive Swagger documentation at `http://localhost:8000/docs`.

**Key Endpoints:**
- `POST /api/pipeline/start` - Initiate a new outreach pipeline
- `GET /api/pipeline/status/{id}` - Poll live pipeline progress
- `POST /api/pipeline/approve` - Approve sending emails after the manual checkpoint
- `GET /api/results/{id}/companies` - Retrieve discovered companies
- `GET /api/export/{id}/full/json` - Export all pipeline data

---

## 🛡️ Resilience & Error Handling

OutreachOS is built for production environments:
- **Intelligent Retries**: Exponential backoff for rate limits and intermittent API failures.
- **Graceful Degradation**: The pipeline continues even if individual contacts fail email resolution.
- **Data Validation**: Strict Pydantic models ensure data consistency across all pipeline stages.

---

## 💻 Technology Stack

**Backend**: Python, FastAPI, HTTPX (Async), Pydantic
**Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons
