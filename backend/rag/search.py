from .embedder import get_embedding
from .qdrant_db import search_qdrant
from .models import SearchResult, SearchResponse
import re
from qdrant_client.models import Filter, FieldCondition, MatchValue

def search_pipeline(query: str, top_k: int = 10) -> SearchResponse:
    # 1. Embed query (Truncate to 1000 chars to avoid CPU quadratic attention hang)
    search_query = query[:1000]
    query_embedding = get_embedding(search_query)
    
    # 2. Semantic Search
    qdrant_results = []
    semantic_results = search_qdrant(query_embedding, top_k=top_k)
    
    # 3. Exact Match Keyword / Number Extraction Fallback
    # If the user specifically mentions a GR number (e.g. 2024111), dense embeddings 
    # might fail to retrieve it because the semantic meaning of surrounding words dominates.
    # We explicitly extract any 4-8 digit number and enforce an exact filter match.
    gr_match = re.search(r'\b(\d{4,8})\b', query)
    if gr_match:
        try:
            gr_no_int = int(gr_match.group(1))
            exact_filter = Filter(
                must=[FieldCondition(key="gr_no", match=MatchValue(value=gr_no_int))]
            )
            exact_results = search_qdrant(query_embedding, top_k=top_k, query_filter=exact_filter)
            if exact_results:
                qdrant_results.extend(exact_results)
                # Drop all semantic results to isolate ONLY this GR
                semantic_results = []
        except Exception:
            pass
            
    # 4. Merge and deduplicate
    seen_ids = set()
    merged_hits = []
    
    for hit in qdrant_results + semantic_results:
        if hit.id not in seen_ids:
            merged_hits.append(hit)
            seen_ids.add(hit.id)
            
    # 5. Format outputs
    results = []
    for hit in merged_hits[:top_k]:
        payload = hit.payload or {}
        results.append(SearchResult(
            gr_no=payload.get("gr_no", 0),
            department=payload.get("department", "Unknown"),
            score=hit.score,
            source_file=payload.get("source_file", ""),
            text=payload.get("text", "")
        ))
        
    return SearchResponse(results=results)
