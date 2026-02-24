from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict
import fitz
import uuid
import httpx
import aiofiles
import json
import re

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

# -------------------------
# CONFIG
# -------------------------
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"
REQUEST_TIMEOUT = 10000

# -------------------------
# APP
# -------------------------
app = FastAPI(title="LLaMA PDF Study Assistant", version="6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# MODEL
# -------------------------
class StudyPlan(BaseModel):
    title: str
    notes: List[str]
    key_concepts: List[str]
    study_recommendations: List[str]
    estimated_study_hours: float
    download_url: str

# -------------------------
# CLEANING HELPERS
# -------------------------
def validate_list(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if isinstance(v, str) and v.strip()]
    return []

def dedupe_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    clean = []
    for item in items:
        key = item.lower().strip()
        if key not in seen:
            seen.add(key)
            clean.append(item.strip())
    return clean

def split_large_notes(notes: List[str]) -> List[str]:
    split_notes = []
    for note in notes:
        if len(note) > 1500:
            parts = re.split(r'\n\n|\.\s+', note)
            split_notes.extend([p.strip() for p in parts if p.strip()])
        else:
            split_notes.append(note.strip())
    return split_notes

def estimate_study_hours(notes: List[str]) -> float:
    # Simple deterministic heuristic:
    # ~12 minutes per detailed note
    hours = len(notes) * 0.2
    return max(1.0, round(hours, 1))

# -------------------------
# PDF GENERATION
# -------------------------
def create_study_pdf(plan: StudyPlan, output_path: Path):
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(plan.title, styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    def add_section(title: str, items: List[str]):
        if not items:
            return
        elements.append(Paragraph(title, styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))
        flow = []
        for item in items:
            formatted = item.replace("\n", "<br/>")
            flow.append(ListItem(Paragraph(formatted, styles["Normal"])))
        elements.append(ListFlowable(flow, bulletType="bullet"))
        elements.append(Spacer(1, 0.4 * inch))

    add_section("Notes", plan.notes)
    add_section("Key Concepts", plan.key_concepts)
    add_section("Study Recommendations", plan.study_recommendations)

    doc.build(elements)

# -------------------------
# PDF TEXT EXTRACTION
# -------------------------
def extract_pdf_text(file_path: Path) -> str:
    doc = fitz.open(file_path)
    text = "\n".join(page.get_text("text") for page in doc)
    doc.close()
    return text.strip()

# -------------------------
# SMART CHUNKING
# -------------------------
def smart_chunk_text(text: str, max_chars: int = 2500) -> List[str]:
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) < max_chars:
            current += p + "\n\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            current = p + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks

# -------------------------
# SAFE JSON EXTRACTION
# -------------------------
def extract_json(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find('{')
        while start != -1:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[start:i + 1])
                        except json.JSONDecodeError:
                            break
            start = text.find('{', start + 1)
    print("FAILED TO PARSE LLM JSON")
    return {}

# -------------------------
# LLM CALL (CHUNK LEVEL ONLY)
# -------------------------
async def call_llm(prompt: str):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_predict": 700  # reduced from 4096
        }
    }

    try:
        timeout = httpx.Timeout(
            connect=20.0,
            read=180.0,   # hard read cap per chunk
            write=20.0,
            pool=20.0
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()

            raw = resp.json().get("response", "").strip()
            return extract_json(raw)

    except httpx.ReadTimeout:
        print("⚠️ Chunk timed out — skipping")
        return {}

    except Exception as e:
        print("⚠️ LLM error:", e)
        return {}

async def summarize_chunk(chunk: str) -> Dict[str, List[str]]:
    prompt = f"""
Return ONLY valid JSON with keys: notes, key_concepts, study_recommendations.
- "notes": list of detailed study notes.
- "key_concepts": list of key terms.
- "study_recommendations": optional study recommendations.

TEXT:
{chunk}
"""
    data = await call_llm(prompt)

    return {
        "notes": validate_list(data.get("notes")),
        "key_concepts": validate_list(data.get("key_concepts")),
        "study_recommendations": validate_list(data.get("study_recommendations"))
    }

# -------------------------
# MAIN PIPELINE
# -------------------------
async def generate_study_plan(text: str, original_filename: str):
    chunks = smart_chunk_text(text)

    all_notes = []
    all_concepts = []
    all_recommendations = []

    for chunk in chunks:
        data = await summarize_chunk(chunk)
        all_notes.extend(data["notes"])
        all_concepts.extend(data["key_concepts"])
        all_recommendations.extend(data["study_recommendations"])

    print(f"TOTAL NOTES: {len(all_notes)}")
    print(f"TOTAL CONCEPTS: {len(all_concepts)}")
    print(f"TOTAL RECOMMENDATIONS: {len(all_recommendations)}")

    # Deterministic cleaning
    clean_notes = split_large_notes(dedupe_preserve_order(all_notes))
    clean_concepts = dedupe_preserve_order(all_concepts)
    clean_recommendations = dedupe_preserve_order(all_recommendations)

    estimated_hours = estimate_study_hours(clean_notes)

    output_pdf = DOWNLOAD_DIR / f"study_{original_filename}"

    plan = StudyPlan(
        title=f"Study Guide – {original_filename}",
        notes=clean_notes,
        key_concepts=clean_concepts,
        study_recommendations=clean_recommendations,
        estimated_study_hours=estimated_hours,
        download_url=f"http://localhost:8000/download/{output_pdf.name}",
    )

    create_study_pdf(plan, output_pdf)

    return plan

# -------------------------
# ROUTES
# -------------------------
@app.post("/upload-pdf", response_model=StudyPlan)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files supported")

    safe_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename

    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            await f.write(chunk)

    text = extract_pdf_text(file_path)
    if not text:
        raise HTTPException(400, "No extractable text found")

    return await generate_study_plan(text, file.filename)

@app.get("/download/{filename}")
async def download_file(filename: str):
    if ".." in filename or "/" in filename:
        raise HTTPException(400, "Invalid filename")

    file_path = DOWNLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, "File not found")

    return FileResponse(file_path, media_type="application/pdf", filename=filename)

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)