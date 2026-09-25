# Nova AI — Full Starter

1. Copy `server/.env.example` to `server/.env`.
2. Put your Perplexity API key and current Perplexity model in `server/.env`.
3. Never upload `.env` to GitHub.

Install server:
```bash
cd server
python -m venv .venv
```
Windows:
```bash
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

In another terminal, from the project root:
```bash
python -m http.server 3000 --directory web
```
Open http://127.0.0.1:3000

Reports are saved in `data/reports.json`.
Before public deployment, protect `/reports`, restrict CORS, add rate limiting, and keep the API key server-side.
