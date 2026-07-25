<div align="center">
  <h1>🏛️ ARA-1 Financial Agent</h1>
  <p><strong>AI-Powered Government Resolution (GR) Drafting Engine</strong></p>
  <p><em>Built for the VJTI Hackathon</em></p>
</div>

<br />

## 📖 Overview

**ARA-1 Financial Agent** is an intelligent document drafting system designed specifically for the Government of Maharashtra. It leverages Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to automate the drafting of complex, formal **Government Resolutions (GRs)** based on past policies, officer decisions, and specific objectives.

By streamlining the conflict-resolution and drafting process, ARA-1 dramatically reduces the administrative burden on government officials while maintaining strict adherence to official formatting and language requirements.

---

## ✨ Key Features

- **🧠 Intelligent Drafting:** Generates structured GRs automatically using advanced LLM reasoning, matching the tone and style of official government documents.
- **📚 RAG-powered Context:** Fetches past resolutions and policies via ChromaDB to ensure newly drafted GRs are legally and historically consistent.
- **⚖️ Automated Conflict Resolution:** Identifies policy conflicts based on previous GRs and allows officers to seamlessly select and justify policy choices before drafting.
- **📄 Document Generation:** Instantly outputs polished `DOCX` and `PDF` files matching the official Government of Maharashtra template layout.
- **🔄 Auto-Ingestion:** Automatically indexes and stores newly generated GRs back into the RAG vector database for future reference.

---

## 🛠️ Tech Stack

### **Backend**
- **Framework:** FastAPI (Python)
- **AI Models:** Groq API (Llama 3 / Mixtral for fast inference)
- **Vector Database:** ChromaDB (with `bge-small-en-v1.5` embeddings via SentenceTransformers)
- **Document Processing:** `python-docx` for Word generation, `PyMuPDF` (fitz) for PDF generation.

### **Frontend**
- **Framework:** React / Next.js (Assumed based on stack)
- **Styling:** CSS / Tailwind CSS 

---

## 🚀 Getting Started

### 1. Backend Setup
Navigate to the `backend` directory and set up your Python environment:
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

Set up your `.env` file in the `backend` directory with your Groq API key:
```env
GROQ_API_KEY=your_api_key_here
```

Start the backend server:
```bash
uvicorn api.main:app --reload
```

### 2. Frontend Setup
Navigate to the `frontend` directory:
```bash
cd frontend
npm install
npm run dev
```

---

## 📂 Project Structure

```text
VJTI_HACKATHON/
│
├── backend/                  # FastAPI Application
│   ├── api/                  # API routes (drafting, downloads)
│   ├── core/                 # Configuration and environment variables
│   ├── models/               # Pydantic data schemas
│   ├── services/             # Core logic (LLM, RAG, Documents, Conflicts)
│   └── templates/            # DOCX templates for GR generation
│
└── frontend/                 # React/Next.js Application
```

---

<div align="center">
  <p>Made with ❤️ for the VJTI Hackathon</p>
</div>