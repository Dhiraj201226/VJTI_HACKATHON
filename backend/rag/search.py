from .embedder import get_embedding
from .qdrant_db import search_qdrant
from .models import SearchResult, SearchResponse

def search_pipeline(query: str, top_k: int = 10) -> SearchResponse:
    query_embedding = get_embedding(query)
    qdrant_results = search_qdrant(query_embedding, top_k=top_k)
    
    results = []
    for hit in qdrant_results:
        payload = hit.payload or {}
        results.append(SearchResult(
            gr_no=payload.get("gr_no", 0),
            score=hit.score,
            source_file=payload.get("source_file", ""),
            text=payload.get("text", "")
        ))
        
    return SearchResponse(results=results)
