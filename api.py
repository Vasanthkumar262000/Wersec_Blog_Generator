"""
FastAPI backend for Wersec Blog Generator.
Run with: uvicorn api:app --reload --port 8000
"""
import asyncio
import os
import pathlib
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from main import (
    _make_llm,
    _research,
    _write_blog,
    _optimize_linkedin_post,
    _slug,
    BlogPostResponse,
)
from tools.image_tool import generate_thumbnail
from tools.linkedin_tool import post_to_linkedin
from tools.whatsapp_tool import send_whatsapp

_executor = ThreadPoolExecutor(max_workers=2)

OUTPUTS_DIR = pathlib.Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)


class GenerateRequest(BaseModel):
    topic: str
    tone: str = "professional"
    length: str = "medium"


class GenerateResponse(BaseModel):
    topic: str
    summary: str
    full_content: str
    sources: list[str]
    tools_used: list[str]
    linkedin_post: str
    thumbnail_url: str | None = None  # e.g. /api/outputs/slug_thumbnail.png


class LinkedInRequest(BaseModel):
    topic: str
    summary: str
    full_content: str
    linkedin_post: str
    thumbnail_filename: str | None = None  # e.g. slug_thumbnail.png


class WhatsAppRequest(BaseModel):
    topic: str
    summary: str
    sources: list[str]


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # cleanup if needed


app = FastAPI(title="Wersec Blog API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


def _run_generate(topic: str, tone: str, word_count: str) -> BlogPostResponse:
    """Blocking blog generation (research + write + LinkedIn). Run in thread pool."""
    llm = _make_llm()
    research = _research(topic, llm)
    result = _write_blog(topic, tone, word_count, research, llm)
    result.linkedin_post = _optimize_linkedin_post(
        result.topic, result.summary, result.full_content, llm
    )
    return result


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    if not req.topic or not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not set. Add it to .env to enable blog generation.",
        )
    topic = req.topic.strip()
    tone = req.tone.lower() if req.tone else "professional"
    length = req.length.lower() if req.length else "medium"
    length_map = {
        "short": "300-500 words",
        "medium": "600-900 words",
        "long": "1000-1400 words",
    }
    word_count = length_map.get(length, "600-900 words")

    try:
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(
                _executor,
                _run_generate,
                topic,
                tone,
                word_count,
            ),
            timeout=300.0,  # 5 min max for research + write + LinkedIn
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Blog generation timed out. Try a simpler topic or try again.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    (OUTPUTS_DIR / f"{_slug(result.topic)}.md").write_text(
        result.full_content, encoding="utf-8"
    )

    thumbnail_url = None
    try:
        thumbnail_path = generate_thumbnail(topic, _slug(result.topic))
        if thumbnail_path and pathlib.Path(thumbnail_path).exists():
            thumbnail_url = f"/api/outputs/{pathlib.Path(thumbnail_path).name}"
    except Exception:
        pass  # thumbnail is optional; don't fail the whole request

    return GenerateResponse(
        topic=result.topic,
        summary=result.summary,
        full_content=result.full_content,
        sources=result.sources or [],
        tools_used=result.tools_used or [],
        linkedin_post=result.linkedin_post or "",
        thumbnail_url=thumbnail_url,
    )


@app.get("/api/outputs/{filename}")
def serve_output(filename: str):
    path = OUTPUTS_DIR / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="image/png" if filename.endswith(".png") else "application/octet-stream")


@app.post("/api/linkedin")
def publish_linkedin(req: LinkedInRequest):
    thumbnail_path = None
    if req.thumbnail_filename:
        p = OUTPUTS_DIR / pathlib.Path(req.thumbnail_filename).name
        if p.exists():
            thumbnail_path = str(p)
    ok = post_to_linkedin(
        topic=req.topic,
        full_content=req.full_content,
        summary=req.summary,
        linkedin_post=req.linkedin_post,
        image_path=thumbnail_path,
    )
    if not ok:
        raise HTTPException(status_code=500, detail="LinkedIn post failed. Check LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN in .env")
    return {"status": "ok"}


@app.post("/api/whatsapp")
def publish_whatsapp(req: WhatsAppRequest):
    ok = send_whatsapp(req.topic, req.summary, req.sources or [])
    if not ok:
        raise HTTPException(status_code=500, detail="WhatsApp failed. Check TWILIO_* credentials in .env")
    return {"status": "ok"}
