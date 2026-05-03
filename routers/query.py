# routers/query.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.rag_service import answer_question

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str
    source_file: Optional[str] = None   # Optional: query a specific PDF


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]
    question: str


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(payload: QuestionRequest):
    """
    Ask a question against indexed PDFs.
    Optionally pass source_file to query a specific PDF only.
    """

    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = answer_question(
            question=payload.question,
            source_file=payload.source_file
        )

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "question": payload.question
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")