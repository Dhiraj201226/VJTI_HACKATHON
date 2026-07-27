from pydantic import BaseModel, Field
from typing import List

class ParsedGR(BaseModel):
    gr_no: int
    department: str
    source_file: str
    language: str
    content: str

class GRChunk(BaseModel):
    gr_no: int
    department: str
    source_file: str
    language: str
    chunk_id: int
    text: str

class QdrantPayload(BaseModel):
    gr_no: int
    department: str
    source_file: str
    language: str
    chunk_id: int
    text: str

class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    gr_no: int
    department: str
    score: float
    source_file: str
    text: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
