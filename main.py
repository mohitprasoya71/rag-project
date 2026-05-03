# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, query

app = FastAPI(
    title="RAG PDF API",
    description="Upload PDFs and ask questions using LangChain + Gemini + Pinecone",
    version="1.0.0"
)

# CORS — allow all origins (restrict in production if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(upload.router, tags=["Upload"])
app.include_router(query.router, tags=["Query"])


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "✅ RAG API is live!",
        "docs": "/docs",
        "endpoints": {
            "upload_pdf": "POST /upload",
            "ask_question": "POST /ask"
        }
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


# Run directly for local dev
if __name__ == "__main__":
    import uvicorn
    from config import APP_HOST, APP_PORT
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)