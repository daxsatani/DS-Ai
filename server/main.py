import os
import json
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Nova AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = Path(__file__).parent.parent / "data" / "reports.json"
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

if not DATA_FILE.exists():
    DATA_FILE.write_text("[]", encoding="utf-8")


class ChatRequest(BaseModel):
    message: str
    language: str = "en"


class ReportRequest(BaseModel):
    message: str
    page: str = "website"


def get_language(code):
    languages = {
        "en": "English",
        "hi": "Hindi",
        "pt": "Brazilian Portuguese",
        "de": "German",
    }
    return languages.get(code, "English")


async def ask_openrouter(message, language):
    api_url = os.getenv("AI_API_URL")
    api_key = os.getenv("AI_API_KEY")
    model = os.getenv("AI_MODEL")
    fallback_model = os.getenv("AI_FALLBACK_MODEL")

    if not api_url or not api_key or not model:
        return (
            "Nova is not configured yet. "
            "Please check the OpenRouter settings in server/.env."
        )

    language_name = get_language(language)

    models = [model]

    if fallback_model and fallback_model != model:
        models.append(fallback_model)

    payload = {
        "models": models,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Nova AI, a helpful multilingual assistant. "
                    f"Answer in {language_name}. "
                    "Be clear, useful and accurate."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                api_url,
                json=payload,
                headers=headers,
            )

        if response.status_code >= 400:
            print(response.text)
            raise HTTPException(
                status_code=502,
                detail="OpenRouter returned an error. Check the server terminal for details.",
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to OpenRouter.",
        )


@app.get("/")
def home():
    return {"name": "Nova AI", "status": "running"}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    reply = await ask_openrouter(
        message,
        request.language,
    )

    return {
        "type": "text",
        "reply": reply,
    }


@app.post("/report")
async def report(request: ReportRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Report cannot be empty.",
        )

    try:
        reports = json.loads(
            DATA_FILE.read_text(encoding="utf-8")
        )
    except Exception:
        reports = []

    reports.append(
        {
            "message": message,
            "page": request.page,
        }
    )

    DATA_FILE.write_text(
        json.dumps(
            reports,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return {
        "ok": True,
        "message": "Report received.",
    }


@app.get("/reports")
def reports():
    try:
        return json.loads(
            DATA_FILE.read_text(encoding="utf-8")
        )
    except Exception:
        return []