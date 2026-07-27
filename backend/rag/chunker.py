from transformers import AutoTokenizer
from typing import Generator
from config import settings
from .models import ParsedGR, GRChunk

# Initialize tokenizer once
tokenizer = AutoTokenizer.from_pretrained(settings.EMBEDDING_MODEL_NAME)
# Suppress the warning about sequences longer than the model's max length 
# since we are deliberately tokenizing long texts just to chunk them down.
tokenizer.model_max_length = 1_000_000

def chunk_text(text: str, chunk_size: int = settings.CHUNK_SIZE, overlap: int = settings.CHUNK_OVERLAP) -> list[str]:
    # Tokenize text to get exact token counts
    tokens = tokenizer.encode(text, add_special_tokens=False)
    
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(tokenizer.decode(chunk_tokens, skip_special_tokens=True))
        
        if end >= len(tokens):
            break
            
        start += (chunk_size - overlap)
        
    return chunks

def chunk_grs(gr_generator: Generator[ParsedGR, None, None]) -> Generator[GRChunk, None, None]:
    for gr in gr_generator:
        chunks = chunk_text(gr.content)
        for i, chunk_text_str in enumerate(chunks):
            yield GRChunk(
                gr_no=gr.gr_no,
                source_file=gr.source_file,
                language=gr.language,
                chunk_id=i + 1,
                text=chunk_text_str
            )
