# services/rag_service.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from services.embedding_service import get_vectorstore
from config import GOOGLE_API_KEY


# Custom prompt to make answers more grounded
RAG_PROMPT_TEMPLATE = """
You are a helpful assistant that answers questions based on the provided context from PDF documents.

Use ONLY the context below to answer the question. 
If the answer is not found in the context, say: "I couldn't find relevant information in the uploaded documents."
Do not make up information.

Context:
{context}

Question: {question}

Answer:
"""

RAG_PROMPT = PromptTemplate(
    template=RAG_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)


def get_llm():
    """Initialize Gemini LLM."""
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3,
        convert_system_message_to_human=True
    )


def answer_question(question: str, source_file: str = None) -> dict:
    """
    Run RAG chain to answer a question.
    Optionally filter by source_file to query a specific PDF.
    Returns answer and source info.
    """
    vectorstore = get_vectorstore()
    llm = get_llm()

    # Build retriever — optionally filter by file
    if source_file:
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 4,
                "filter": {"source_file": source_file}
            }
        )
    else:
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )

    # Build QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": RAG_PROMPT}
    )

    result = qa_chain.invoke({"query": question})

    # Extract unique source files from retrieved docs
    sources = list(set([
        doc.metadata.get("source_file", "unknown")
        for doc in result.get("source_documents", [])
    ]))

    return {
        "answer": result["result"],
        "sources": sources
    }