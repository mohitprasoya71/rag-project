# services/pdf_service.py
import os
import tempfile
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET


def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_pdf_to_supabase(file_bytes: bytes, filename: str) -> str:
    """
    Upload a PDF to Supabase Storage.
    Returns the public URL of the uploaded file.
    """
    supabase = get_supabase_client()

    # Upload to Supabase storage bucket
    response = supabase.storage.from_(SUPABASE_BUCKET).upload(
        path=filename,
        file=file_bytes,
        file_options={"content-type": "application/pdf", "upsert": "true"}
    )

    # Get public URL
    public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
    return public_url


def save_temp_pdf(file_bytes: bytes) -> str:
    """
    Save PDF bytes to a temp file.
    Returns the temp file path.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(file_bytes)
    tmp.close()
    return tmp.name