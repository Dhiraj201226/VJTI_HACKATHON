import os
from typing import Generator
from config import settings
from .models import ParsedGR

def extract_real_department(content_lines: list[str]) -> str:
    # Scan the first 25 lines of the GR content to find the real department name
    for line in content_lines[:25]:
        line_clean = line.strip()
        if "Department" in line_clean and "Resolution" not in line_clean and "Circular" not in line_clean:
            return line_clean
    return "Unknown Department"

def parse_grs(filepath: str = settings.DATASET_PATH, start_from_gr: int = 0) -> Generator[ParsedGR, None, None]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
    
    delimiter = "=" * 100
    
    with open(filepath, 'r', encoding='utf-8') as f:
        current_gr_no = None
        current_source = None
        current_content = []
        state = "SEARCHING"
        
        for line in f:
            line_stripped = line.strip()
            
            if line_stripped == delimiter:
                if state == "SEARCHING":
                    state = "IN_HEADER"
                elif state == "IN_HEADER":
                    state = "IN_CONTENT"
                elif state == "IN_CONTENT":
                    # Reached the delimiter of the NEXT GR
                    if current_gr_no is not None and current_gr_no > start_from_gr:
                        yield ParsedGR(
                            gr_no=current_gr_no,
                            department=extract_real_department(current_content),
                            source_file=current_source or "",
                            language="en",
                            content="".join(current_content).strip()
                        )
                    
                    # Reset for next GR
                    current_gr_no = None
                    current_source = None
                    current_content = []
                    state = "IN_HEADER"
                continue
                
            if state == "IN_HEADER":
                if line_stripped.startswith("GR No."):
                    parts = line_stripped.split(":", 1)
                    if len(parts) > 1:
                        try:
                            current_gr_no = int(parts[1].strip())
                        except ValueError:
                            current_gr_no = 0
                elif line_stripped.startswith("Source File"):
                    parts = line_stripped.split(":", 1)
                    if len(parts) > 1:
                        current_source = parts[1].strip()
                        
            elif state == "IN_CONTENT":
                if current_gr_no is not None and current_gr_no > start_from_gr:
                    current_content.append(line)
                
        # Yield the very last GR
        if state == "IN_CONTENT" and current_gr_no is not None and current_gr_no > start_from_gr:
            yield ParsedGR(
                gr_no=current_gr_no,
                department=extract_real_department(current_content),
                source_file=current_source or "",
                language="en",
                content="".join(current_content).strip()
            )
