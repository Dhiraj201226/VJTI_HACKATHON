from fastapi import FastAPI, BackgroundTasks
from rag.models import SearchRequest, SearchResponse, ChatRequest, ChatResponse
from rag.search import search_pipeline
from rag.ingest import ingest_pipeline
from rag.qdrant_db import client
from rag.llm import generate_answer
from config import settings

app = FastAPI(title=settings.PROJECT_NAME)


@app.post("/ingest")
def trigger_ingestion(background_tasks: BackgroundTasks):
    background_tasks.add_task(ingest_pipeline)
    return {"message": "Ingestion started in the background."}


@app.get("/qdrant-status")
def qdrant_status():
    info = client.get_collection(settings.COLLECTION_NAME)
    return {
        "collection": settings.COLLECTION_NAME,
        "points": info.points_count
    }


@app.post("/search", response_model=SearchResponse)
def search_grs(request: SearchRequest):
    return search_pipeline(request.query)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return generate_answer(request.query, request.top_k)