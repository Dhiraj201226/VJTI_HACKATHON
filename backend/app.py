from fastapi import FastAPI, BackgroundTasks
from rag.models import SearchRequest, SearchResponse
from rag.search import search_pipeline
from rag.ingest import ingest_pipeline
from config import settings

app = FastAPI(title=settings.PROJECT_NAME)

@app.api_route("/ingest", methods=["GET", "POST"])
def trigger_ingestion(background_tasks: BackgroundTasks):
    """
    Starts the full manual ingestion pipeline.
    Runs in the background to avoid blocking the API for 100,000 GRs.
    """
    background_tasks.add_task(ingest_pipeline)
    return {"message": "Ingestion started in the background."}

@app.post("/search", response_model=SearchResponse)
def search_grs(request: SearchRequest):
    """
    Searches the Qdrant database for the top matching GR chunks.
    """
    response = search_pipeline(request.query)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
