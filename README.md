# Study Planner

A modern web application that transforms PDFs into organized study materials using Next.js, Tailwind CSS, and FastAPI.

## Features

✨ **PDF to Notes**: Upload any PDF and automatically extract and organize content into study notes
📚 **Key Concepts**: AI-powered extraction of important concepts and terms
💡 **Study Recommendations**: Personalized study tips and strategies
⏱️ **Time Estimates**: Automatic estimation of study time needed
🎨 **Beautiful UI**: Clean, intuitive interface built with Tailwind CSS

## Tech Stack

### Frontend

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API requests

### Backend

- **FastAPI** - Modern Python web framework
- **PyMuPDF (fitz)** - PDF text extraction
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- pip

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

The backend will run at `http://localhost:8000`

API Documentation available at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will run at `http://localhost:3000`

## Usage

1. Open `http://localhost:3000` in your browser
2. Upload a PDF file or drag and drop it onto the upload area
3. Wait for processing to complete
4. View extracted notes, key concepts, and study recommendations
5. Switch between tabs to explore different study materials
6. Use study tips to optimize your learning

## API Endpoints

### POST `/upload-pdf`

Upload and process a PDF file

**Request**: Form data with file
**Response**: Study plan with notes, concepts, and recommendations

### POST `/analyze-text`

Analyze plain text and generate study materials

**Request**: `{"text": "your text here"}`
**Response**: Study plan object

### GET `/study-tips/{subject}`

Get personalized study tips for a subject

**Parameters**: subject (math, science, history, language)
**Response**: List of study tips

## Project Structure

```
study_planner/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example         # Environment variables
│   └── uploads/             # Temporary PDF storage
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Home page
│   │   ├── layout.tsx       # Root layout
│   │   └── globals.css      # Global styles
│   ├── components/
│   │   ├── PdfUploader.tsx  # Upload component
│   │   └── StudyPlanDisplay.tsx  # Results display
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── next.config.js
└── README.md
```

## Features Coming Soon

- 🔐 User authentication and profiles
- 💾 Save study materials to cloud
- 🤖 AI-powered note generation using OpenAI API
- 📊 Study progress tracking
- 🎯 Quiz generation from notes
- 👥 Collaborative study groups
- 📱 Mobile app support

## Environment Variables

### Backend (.env)

```
OPENAI_API_KEY=your_api_key_here
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT

## Support

For issues or questions, please open an issue in the repository.

---

Happy studying! 📚✨
# Studie_Pdf_maker
