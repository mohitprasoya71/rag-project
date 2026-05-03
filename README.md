# 📄 RAG PDF API

A production-ready **RAG (Retrieval Augmented Generation)** API — upload any PDF and ask questions about it in natural language. Built and deployed after 5+ failed builds and real debugging battles. 💪

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **FastAPI** | REST API framework |
| **LangChain** | RAG pipeline & chains |
| **Google Gemini** (`gemini-1.5-flash`) | LLM + Embeddings |
| **Pinecone** | Vector database (persistent) |
| **Supabase** | PDF file storage (persistent) |
| **Render** | Deployment platform |

---

## ⚙️ How It Works

```
POST /upload  →  PDF saved to Supabase
              →  PDF chunked & embedded via Gemini
              →  Vectors stored in Pinecone

POST /ask     →  Pinecone retrieves relevant chunks
              →  Gemini generates answer
              →  Returns answer + source file name
```

---

## 📁 Project Structure

```
rag-project/
├── main.py                  # FastAPI app entry point
├── config.py                # All environment variables
├── requirements.txt         # Python dependencies
├── .env.example             # Template for your .env file
├── .python-version          # Forces Python 3.11 on Render
├── .gitignore
├── Procfile                 # Render start command
│
├── services/
│   ├── pdf_service.py       # PDF upload + Supabase storage
│   ├── embedding_service.py # Chunking + Pinecone indexing
│   └── rag_service.py       # RAG chain + question answering
│
└── routers/
    ├── upload.py            # POST /upload endpoint
    └── query.py             # POST /ask endpoint
```

---

## 📌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/health` | Simple status check |
| GET | `/docs` | Swagger UI |
| POST | `/upload` | Upload a PDF |
| POST | `/ask` | Ask a question |

---

## 📤 POST /upload

Upload a PDF to be indexed.

**Request:** `multipart/form-data`
```
file: your_document.pdf
```

**Response:**
```json
{
  "message": "✅ 'your_document.pdf' uploaded and indexed successfully!",
  "filename": "your_document.pdf",
  "chunks_indexed": 42,
  "storage_url": "https://..."
}
```

---

## ❓ POST /ask

Ask a question against indexed PDFs.

**Request:**
```json
{
  "question": "What does Meticulous mean?",
  "source_file": null
}
```

**Response:**
```json
{
  "answer": "Meticulous means showing great attention to detail.",
  "sources": ["your_document.pdf"],
  "question": "What does Meticulous mean?"
}
```

---

## ⚠️ IMPORTANT: How to use `source_file`

The `source_file` field must be the **exact filename** of the PDF you uploaded — including the `.pdf` extension.

```json
✅ Correct:
{
  "question": "Summarize this document",
  "source_file": "mohit.pdf"
}

❌ Wrong — missing extension:
{
  "question": "Summarize this document",
  "source_file": "mohit"
}

❌ Wrong — incorrect filename:
{
  "question": "Summarize this document",
  "source_file": "document.pdf"
}
```

> 💡 **Tip:** The exact filename is returned in the `/upload` response under `"filename"`. Copy it from there and paste it into `source_file` in `/ask`.

To **search across ALL uploaded PDFs** at once, set `source_file` to `null`:
```json
{
  "question": "What topics are covered?",
  "source_file": null
}
```

---

## 🐛 Errors Faced & Fixed

| Error | Cause | Fix |
|---|---|---|
| `ImportError: RetrievalQA` | Wrong import path in newer LangChain | Changed to `from langchain.chains import RetrievalQA` |
| `resolution-too-deep` | Too many unpinned packages conflicting | Pinned versions in `requirements.txt` |
| `langchain-pinecone not found` | Version didn't exist on Render's pip | Updated to correct available version |
| `ResolutionImpossible` ⭐ **Toughest** | Pinned versions conflicting with each other | Removed ALL version pins, let pip auto-resolve |
| `ModuleNotFoundError: routers` | Missing `__init__.py` or wrong run directory | Added `__init__.py` to `routers/` and `services/` |

> ⭐ **Toughest error:** `ResolutionImpossible` — every pinned version fix broke something else. The fix was counterintuitive: remove all pins and trust pip to figure it out automatically.

---

## 📝 Notes

- **Free tier cold starts**: Render free tier sleeps after 15 mins — first request may take ~30 seconds
- **PDF size limit**: 10MB max per upload
- **Pinecone free tier**: 1 index, up to 100K vectors
- **Supabase free tier**: 1GB storage
- **Data persistence**: Both Pinecone and Supabase are persistent — data survives Render restarts
