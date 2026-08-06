import os
import sys
from typing import Generator
from config import settings
from .models import ParsedGR

# Import the fuzzy matcher from the root backend directory
try:
    from remap_departments import get_best_match
except ImportError:
    # If parser.py is run from a different directory, try adding the parent directory to sys.path
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from remap_departments import get_best_match

from .classifier import classify_department_with_llm

def extract_real_department(content_lines: list[str]) -> str:
    # Scan the first 100 lines of the GR content to find the real department name
    for line in content_lines[:100]:
        line_lower = line.lower()
        if ("department" in line_lower or "विभाग" in line_lower) and "resolution" not in line_lower and "circular" not in line_lower and "निर्णय" not in line_lower:
            if len(line.split()) <= 20:
                return line.strip()
    return "Unknown Department"

def parse_grs(filepath: str = settings.DATASET_PATH, start_from_gr: int = 0) -> Generator[ParsedGR, None, None]:
    if not os.path.exists(filepath):
        print(f"Dataset not found at {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        current_gr_no = None
        current_department = None
        current_source = None
        current_content = []
        state = "SEARCHING"
        
        for line in f:
            line_stripped = line.strip()
            
            # End of GR check (Only valid if we are actively reading content)
            if line_stripped == "=" * 100:
                if state == "CONTENT":
                    if current_gr_no is not None and current_gr_no > start_from_gr:
                        raw_dept = current_department or extract_real_department(current_content)
                        mapped_dept = get_best_match(raw_dept)
                        
                        gr_text = "".join(current_content).strip()
                        
                        if not mapped_dept:
                            # Fallback to LLM classification
                            mapped_dept = classify_department_with_llm(gr_text)
                        
                        if mapped_dept:
                            yield ParsedGR(
                                gr_no=current_gr_no,
                                department=mapped_dept,
                                source_file=current_source or "",
                                language="mr" if "marathi" in filepath else "en",
                                content=gr_text
                            )
                        else:
                            # Yield with a special flag or just a dummy department to indicate it's skipped
                            # Let's yield it with department "SKIPPED_BY_AI" so ingest.py can count and drop it
                            yield ParsedGR(
                                gr_no=current_gr_no,
                                department="SKIPPED_BY_AI",
                                source_file=current_source or "",
                                language="mr" if "marathi" in filepath else "en",
                                content=""
                            )
                    # Reset variables for next GR
                    current_gr_no = None
                    current_department = None
                    current_source = None
                    current_content = []
                    state = "SEARCHING"
                continue
                
            # If we see GR No. we definitively enter HEADER state
            if line_stripped.startswith("GR No."):
                state = "HEADER"
                parts = line_stripped.split(":", 1)
                if len(parts) > 1:
                    try:
                        current_gr_no = int(parts[1].strip())
                    except ValueError:
                        current_gr_no = 0
            
            elif state == "HEADER":
                if line_stripped.startswith("Department"):
                    parts = line_stripped.split(":", 1)
                    if len(parts) > 1:
                        current_department = parts[1].strip()
                elif line_stripped.startswith("Source File"):
                    parts = line_stripped.split(":", 1)
                    if len(parts) > 1:
                        current_source = parts[1].strip()
                elif line_stripped.startswith("# Page"):
                    # This marks the beginning of content!
                    state = "CONTENT"
                    current_content.append(line)
                    
            elif state == "CONTENT":
                current_content.append(line)
                
        # Yield the very last GR if file ends without final ====
        if state == "CONTENT" and current_gr_no is not None and current_gr_no > start_from_gr:
            raw_dept = current_department or extract_real_department(current_content)
            mapped_dept = get_best_match(raw_dept)
            gr_text = "".join(current_content).strip()
            
            if not mapped_dept:
                mapped_dept = classify_department_with_llm(gr_text)
                
            if mapped_dept:
                yield ParsedGR(
                    gr_no=current_gr_no,
                    department=mapped_dept,
                    source_file=current_source or "",
                    language="mr" if "marathi" in filepath else "en",
                    content=gr_text
                )
            else:
                yield ParsedGR(
                    gr_no=current_gr_no,
                    department="SKIPPED_BY_AI",
                    source_file=current_source or "",
                    language="mr" if "marathi" in filepath else "en",
                    content=""
                )
