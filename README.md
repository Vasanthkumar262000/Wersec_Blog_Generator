# Wersec Blog Generator

AI-powered cybersecurity blog generator with LinkedIn and WhatsApp publishing. Two UIs: **React (recommended)** and legacy Streamlit.

## React app (recommended)

The React UI renders correctly with no raw HTML issues. Run the API and the frontend:

### 1. Backend (Python API)

```bash
# Create venv and install deps (if not already)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the API (port 8000)
uvicorn api:app --reload --port 8000
```

### 2. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The app proxies `/api` to the backend.

### One-time setup

- Copy `.env.example` to `.env` and set:
  - `GROQ_API_KEY` (required for blog generation)
  - `GOOGLE_API_KEY` (optional, for thumbnail)
  - `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_PERSON_URN` (optional, for LinkedIn)
  - `TWILIO_*` (optional, for WhatsApp)

---

## Legacy Streamlit app

```bash
source venv/bin/activate
streamlit run app.py
```

Or use the script (uses `venv` or `.venv` if it has Streamlit):

```bash
./run.sh
```

---

## Project layout

- `api.py` — FastAPI backend (generate, LinkedIn, WhatsApp)
- `frontend/` — React + Vite + Tailwind UI
- `app.py` — Streamlit UI (legacy)
- `main.py` — LLM pipeline (research, write, LinkedIn optimize)
- `tools/` — image, LinkedIn, WhatsApp helpers
