# Development Guide

## Getting Started

### Option 1: Manual Setup (Recommended for Development)

#### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend runs on: http://localhost:8000

View API docs at: http://localhost:8000/docs

#### Frontend (in a new terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:3000

### Option 2: Using Startup Script

```bash
chmod +x start.sh
./start.sh
```

Or with Docker:

```bash
./start.sh docker
```

### Option 3: Docker Compose

```bash
docker-compose up
```

## Project Structure

### Backend (FastAPI)

**Main entry point**: [backend/main.py](backend/main.py)

Key functions:

- `extract_text_from_pdf()` - Extracts text from PDF files
- `generate_notes_and_plan()` - Creates study materials from text
- POST `/upload-pdf` - Main endpoint for PDF processing
- POST `/analyze-text` - Analyze plain text
- GET `/study-tips/{subject}` - Get subject-specific tips

**Dependencies**:

- `fastapi` - Web framework
- `pydantic` - Data validation
- `pymupdf` - PDF processing
- `uvicorn` - ASGI server

### Frontend (Next.js + Tailwind)

**Entry point**: [frontend/app/page.tsx](frontend/app/page.tsx)

**Components**:

- [PdfUploader.tsx](frontend/components/PdfUploader.tsx) - File upload with drag & drop
- [StudyPlanDisplay.tsx](frontend/components/StudyPlanDisplay.tsx) - Results display with tabs

**Styling**: [Tailwind CSS](frontend/tailwind.config.js)

## API Reference

### POST /upload-pdf

Upload and process a PDF file.

**Request:**

```bash
curl -X POST -F "file=@document.pdf" http://localhost:8000/upload-pdf
```

**Response:**

```json
{
  "success": true,
  "filename": "document.pdf",
  "study_plan": {
    "title": "Study Plan",
    "notes": ["note1", "note2", ...],
    "key_concepts": ["concept1", "concept2", ...],
    "study_recommendations": ["tip1", "tip2", ...],
    "estimated_study_hours": 2.5
  }
}
```

### POST /analyze-text

Analyze plain text instead of uploading a PDF.

**Request:**

```bash
curl -X POST http://localhost:8000/analyze-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text content here..."}'
```

### GET /study-tips/{subject}

Get study recommendations for a subject.

**Supported subjects**: math, science, history, language

**Request:**

```bash
curl http://localhost:8000/study-tips/math
```

**Response:**

```json
{
  "subject": "math",
  "tips": [
    "Practice problems daily",
    "Work through examples step by step",
    ...
  ]
}
```

## Development Tips

### Backend Development

1. The FastAPI docs are auto-generated. Visit http://localhost:8000/docs while the server is running
2. To reload the server on file changes, use: `uvicorn main:app --reload`
3. PDF files are saved to `backend/uploads/` directory
4. Check [requirements.txt](backend/requirements.txt) for all dependencies

### Frontend Development

1. Hot reload is enabled by default with `npm run dev`
2. TypeScript is configured for type safety
3. Tailwind CSS classes are used for styling
4. Check [package.json](frontend/package.json) for all dependencies

## Next Steps & Features to Add

- [ ] OpenAI integration for AI-powered note generation
- [ ] User authentication (Firebase, Auth0, etc.)
- [ ] Database integration (SQLAlchemy, PostgreSQL)
- [ ] Export functionality (PDF, DOCX, Markdown)
- [ ] Quiz generation from notes
- [ ] Study progress tracking
- [ ] Spaced repetition recommendations
- [ ] Dark mode support
- [ ] Mobile app (React Native)

## Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000
# Kill the process if needed
kill -9 <PID>
```

### Frontend won't start

```bash
# Clear Next.js cache
rm -rf frontend/.next
npm run dev
```

### PDF upload fails

- Ensure the PDF file is valid
- Check that the `uploads/` directory exists and is writable
- Check backend logs for error messages

### CORS errors

- Verify `NEXT_PUBLIC_API_URL` is set correctly in frontend `.env.local`
- Check that backend CORS middleware is properly configured

## Environment Setup

Create these files for configuration:

**backend/.env**:

```
OPENAI_API_KEY=your_key_here
FRONTEND_URL=http://localhost:3000
```

**frontend/.env.local**:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)

---

Happy coding! 🚀
