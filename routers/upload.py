# routers/upload.py
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.pdf_service import upload_pdf_to_supabase, save_temp_pdf
from services.embedding_service import load_and_chunk_pdf, embed_and_store

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file.
    - Stores original PDF in Supabase Storage
    - Parses, chunks, embeds and stores vectors in Pinecone
    """

    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Validate file size (max 10MB)
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")

    tmp_path = None
    try:
        # 1. Upload PDF to Supabase Storage
        pdf_url = upload_pdf_to_supabase(file_bytes, file.filename)

        # 2. Save PDF temporarily for LangChain to parse
        tmp_path = save_temp_pdf(file_bytes)

        # 3. Load and chunk the PDF
        chunks = load_and_chunk_pdf(tmp_path)

        if not chunks:
            raise HTTPException(status_code=422, detail="Could not extract text from PDF.")

        # 4. Embed chunks and store in Pinecone
        num_chunks = embed_and_store(chunks, file.filename)

        return {
            "message": f"✅ '{file.filename}' uploaded and indexed successfully!",
            "filename": file.filename,
            "chunks_indexed": num_chunks,
            "storage_url": pdf_url
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    finally:
        # Always clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)