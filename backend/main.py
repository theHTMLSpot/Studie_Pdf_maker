from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
import fitz  # PyMuPDF
import uuid
import httpx
import asyncio
import aiofiles
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# -------------------------
# CONFIG
# -------------------------
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

OLLAMA_URL = "http://localhost:11434/api/generate"

# -------------------------
# APP SETUP
# -------------------------
app = FastAPI(title="LLaMA PDF Study Assistant", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production frontend
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# MODELS
# -------------------------
class StudyPlan(BaseModel):
    title: str
    notes: list[str]
    key_concepts: list[str]
    study_recommendations: list[str]
    estimated_study_hours: float
    download_url: str

# -------------------------
# UTILITIES
# -------------------------
def create_study_pdf(plan: StudyPlan, output_path: Path):
    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, plan.title)

    # Notes
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Notes")
    y -= 20
    c.setFont("Helvetica", 11)
    for note in plan.notes:
        for line in note.splitlines():
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 11)
            c.drawString(60, y, f"- {line}")
            y -= 15
        y -= 10

    # Key Concepts
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Key Concepts")
    y -= 20
    c.setFont("Helvetica", 11)
    for concept in plan.key_concepts:
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 11)
        c.drawString(60, y, f"- {concept}")
        y -= 15

    # Study Recommendations
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Study Recommendations")
    y -= 20
    c.setFont("Helvetica", 11)
    for rec in plan.study_recommendations:
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 11)
        c.drawString(60, y, f"- {rec}")
        y -= 15

    c.save()

def extract_pdf_text(file_path: Path) -> str:
    doc = fitz.open(file_path)
    text = "\n".join(page.get_text("text") for page in doc)
    doc.close()
    return text.strip()

def chunk_text(text: str, max_chars: int = 3000) -> list[str]:
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

# -------------------------
# LLaMA INTERACTION
# -------------------------
async def process_chunk(client: httpx.AsyncClient, chunk: str) -> dict:
    prompt = f"""
You are a school professor helping students create study guides from textbook content.

Read the following text and do the following:
1. Identify the topic and subject area.
2. Create concise study notes covering one core concept each.
- Each note must be at least 3 lines and at most 5 lines.
- Produce up to 10 notes per chunk.
- Across the entire text, produce at most 15 notes.
- Use only examples that appear in the text if needed.
3. Extract the main key concepts (names or terms).
4. Give study recommendations.

HARD RULES:
- ALL output must be in the SAME LANGUAGE as the input text. 
- DO NOT use English words if the input text is not English. 
- DO NOT use headings, titles, or labels.
- Each note is a factual statement, not a question or task.
- Do not reference exercises, assignments, questions, images, or sources outside the text.
- Always produce notes, even if the text is short.
- These rules are for notes, concepts, and recommendations.

OUTPUT FORMAT (STRICT):
Estimated Study Hours: X.Y
---
Notes:
- note title
note content line 1
note content line 2
note content line 3
--end-note--
- next note title
note content
--end-note--
---
Key Concepts:
- concept 1
- concept 2
---
Study Recommendations:
- recommendation 1
- recommendation 2

TEXT:
{chunk}
"""

    payload = {"model": "llama3", "prompt": prompt, "stream": False}

    try:
        resp = await client.post(OLLAMA_URL, json=payload)
        resp.raise_for_status()
        raw = resp.json().get("response", "")
        print("Ollama raw response:", raw[:500])  # debug
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"Ollama error: {e}")
        return {"notes": [], "concepts": [], "recommendations": [], "estimated_hours": 1.0}

    notes, concepts, recommendations = [], [], []
    estimated_hours = 1.0  # default

    # Extract Estimated Study Hours first
    import re
    m = re.search(r"Estimated Study Hours:\s*([0-9]+(?:\.[0-9]+)?)", raw)
    if m:
        estimated_hours = float(m.group(1))
        raw = raw.replace(m.group(0), "")

    # Split remaining content into sections
    sections = [s.strip() for s in raw.split("---") if s.strip()]
    for section in sections:
        lines = [l.strip() for l in section.splitlines() if l.strip()]
        if not lines:
            continue
        header = lines[0].lower()
        # Notes
        if "notes" in header:
            current_note = []
            for line in lines[1:]:
                if line == "--end-note--":
                    if current_note:
                        # enforce 3-5 lines per note
                        note_lines = current_note[:5]
                        while len(note_lines) < 3:
                            note_lines.append("")  # pad short notes
                        notes.append("\n".join(note_lines))
                        current_note = []
                else:
                    current_note.append(line)
            if current_note:
                note_lines = current_note[:5]
                while len(note_lines) < 3:
                    note_lines.append("")
                notes.append("\n".join(note_lines))
        # Key Concepts
        elif "key concepts" in header:
            for line in lines[1:]:
                if line.startswith("- "):
                    concepts.append(line[2:].strip())
        # Study Recommendations
        elif "study recommendations" in header:
            for line in lines[1:]:
                if line.startswith("- "):
                    recommendations.append(line[2:].strip())

    return {
        "notes": notes,
        "concepts": concepts,
        "recommendations": recommendations,
        "estimated_hours": estimated_hours,
    }

async def generate_study_plan(text: str, original_filename: str) -> StudyPlan:
    chunks = chunk_text(text)
    notes, key_concepts, recommendations = [], [], []

    async with httpx.AsyncClient(timeout=120) as client:
        tasks = [process_chunk(client, c) for c in chunks[:10]]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                continue
            notes.extend(r["notes"])
            key_concepts.extend(r["concepts"])
            recommendations.extend(r["recommendations"])

    # enforce max 15 notes total
    notes = notes[:15]

    estimated_hours = max(1.0, len(chunks) * 1.5)

    output_pdf = DOWNLOAD_DIR / f"study_{original_filename}"

    plan = StudyPlan(
        title=f"Study Guide – {original_filename}",
        notes=notes,
        key_concepts=list(dict.fromkeys(key_concepts))[:20],
        study_recommendations=recommendations[:10],
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
        raise HTTPException(400, "Only PDF files are supported")

    safe_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename

    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            await f.write(chunk)

    text = extract_pdf_text(file_path)
    if not text:
        raise HTTPException(400, "No extractable text found in PDF")

    return await generate_study_plan(text, file.filename)

@app.get("/download/{filename}")
async def download_file(filename: str):
    if ".." in filename or "/" in filename:
        raise HTTPException(400, "Invalid filename")

    file_path = DOWNLOAD_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(404, "File not found")

    return FileResponse(file_path, media_type="application/pdf", filename=filename)

# -------------------------
# DEV ENTRYPOINT
# -------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
