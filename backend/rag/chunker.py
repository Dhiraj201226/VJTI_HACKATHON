from typing import Generator
from config import settings
from .models import ParsedGR, GRChunk

def chunk_text(text: str, chunk_size: int = settings.CHUNK_SIZE, overlap: int = settings.CHUNK_OVERLAP) -> list[str]:
    """
    Blazingly fast chunking using word splitting instead of huggingface tokenization.
    Assumes ~0.75 words per token for English/Marathi mixed text.
    """
    chunk_size_words = int(chunk_size * 0.75)
    overlap_words = int(overlap * 0.75)
    
    words = text.split()
    chunks = []
    start = 0
    
    while start < len(words):
        end = start + chunk_size_words
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        
        if end >= len(words):
            break
            
        start += (chunk_size_words - overlap_words)
        
    return chunks

def chunk_grs(gr_generator: Generator[ParsedGR, None, None]) -> Generator[GRChunk, None, None]:
    for gr in gr_generator:
        chunks = chunk_text(gr.content)
        for i, chunk_text_str in enumerate(chunks):
            yield GRChunk(
                gr_no=gr.gr_no,
                department=gr.department,
                source_file=gr.source_file,
                language=gr.language,
                chunk_id=i + 1,
                text=chunk_text_str
            )
