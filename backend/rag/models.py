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

class SearchResult(BaseModel):
    gr_no: int
    department: str
    score: float
    source_file: str
    text: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    history: List[ChatMessage] = []
    top_k: int = 5

class ChatResponse(BaseModel):
    answer: str
    sources: List[SearchResult]

class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
