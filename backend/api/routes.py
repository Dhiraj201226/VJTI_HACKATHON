from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from models.schemas import DraftRequest, GenerateRequest, FinalDraftResponse, LLMDraftResponse
from rag.search import search_pipeline
from services.conflict_service import detect_conflicts
from services.llm_service import generate_gr_json
from services.document_service import generate_documents
import os
import hashlib
from rag.qdrant_db import upload_chunks
from rag.embedder import get_embedding
from rag.models import GRChunk
from db.database import SessionLocal
from db.models import GeneratedGR

router = APIRouter()

def string_to_int(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % 10000000

def get_qdrant_results_as_dict(objective: str, top_k: int = 3):
    search_response = search_pipeline(objective, top_k=top_k)
    docs = []
    metas = []
    for res in search_response.results:
        docs.append(res.text)
        metas.append({
            "gr_number": res.gr_no,
            "department": res.department,
            "date": "2023-01-01", # Placeholder since Qdrant payload might not have date
            "policy_area": res.department # Use department as policy area proxy
        })
    return {"documents": [docs], "metadatas": [metas]}

@router.post("/draft/initiate")
def initiate_draft(request: DraftRequest):
    objective = request.objective
    
    # 1. Retrieve chunks from Qdrant
    results = get_qdrant_results_as_dict(objective, top_k=3)
    
    # 2. Conflict detection
    conflicts = detect_conflicts(results)
    
    # 3. If conflicts exist, return them for officer resolution
    if conflicts:
        return {
            "status": "conflicts_detected",
            "conflicts": [c.dict() for c in conflicts],
            "retrieved_context": results
        }
        
    # No conflicts, we could auto-generate, but let's return context to frontend to hit generate next
    return {
        "status": "ready",
        "conflicts": [],
        "retrieved_context": results
    }

from services.reference_parser import extract_and_verify_references
from services.glossary_service import check_terminology

@router.post("/draft/generate", response_model=FinalDraftResponse)
def generate_draft(request: GenerateRequest):
    # Re-retrieve or use passed context
    results = get_qdrant_results_as_dict(request.objective, top_k=3)
    
    # Generate JSON from LLM
    json_response = generate_gr_json(request.objective, results, request.officer_decisions)
    
    # Phase 2.4: Template Enforcement Validation
    template = json_response.template_fields
    warnings = []
    if not template.subject: warnings.append("Missing Subject")
    if not template.body: warnings.append("Missing Preamble/Body")
    if not template.signature: warnings.append("Missing Signature")
    if not template.financial_implications: warnings.append("Missing Budget/Financial Details")
    
    # Extract raw text from body and clauses for analysis
    body_text = " ".join(template.body) if isinstance(template.body, list) else str(template.body)
    clauses_text = " ".join(template.clauses) if isinstance(template.clauses, list) else str(template.clauses)
    full_text = f"{body_text} {clauses_text}"
    
    # Phase 2.1: Reference Parsing
    reference_data = extract_and_verify_references(full_text)
    
    # Phase 2.3: Terminology Checker
    terminology_suggestions = check_terminology(full_text)
    
    # We will inject these analysis results into a custom field
    json_response.phase2_analysis = {
        "template_warnings": warnings,
        "references": reference_data,
        "terminology": terminology_suggestions
    }
    
    # Generate Documents
    docx_path, pdf_path = generate_documents(json_response)
    
    # Save to SQLite Database
    fields = json_response.template_fields
    db = SessionLocal()
    try:
        new_gr = GeneratedGR(
            gr_number=fields.gr_number,
            department=fields.department,
            subject=fields.subject,
            date=fields.date,
            docx_path=docx_path,
            pdf_path=pdf_path
        )
        db.add(new_gr)
        db.commit()
    except Exception as e:
        print(f"Error saving to SQLite database: {e}")
        db.rollback()
    finally:
        db.close()
    
    # Store generated GR in RAG
    fields = json_response.template_fields
    body_text = " ".join(fields.body) if isinstance(fields.body, list) else str(fields.body)
    doc_text = f"Government Resolution regarding {fields.subject}. {body_text} Dept: {fields.department}. Date: {fields.date}. GR: {fields.gr_number}"
    
    try:
        from rag.embedder import get_embedding
        from rag.qdrant_db import upload_chunks
        from rag.models import GRChunk
        import random
        
        # Try to extract an integer from gr_number for the DB schema, else random
        gr_no_str = ''.join(filter(str.isdigit, str(fields.gr_number)))
        gr_no_int = int(gr_no_str) if gr_no_str else random.randint(100000, 999999)
        
        chunk = GRChunk(
            gr_no=gr_no_int,
            department=fields.department,
            source_file="Generated_AI_Draft",
            language="en",
            chunk_id=1,
            text=doc_text
        )
        
        embedding = get_embedding(doc_text)
        upload_chunks([chunk], [embedding])
        print(f"Successfully saved GR {fields.gr_number} to Qdrant")
    except Exception as e:
        print(f"Error adding to RAG: {e}")
    
    return FinalDraftResponse(
        docx_url=f"/api/download/{os.path.basename(docx_path)}",
        pdf_url=f"/api/download/{os.path.basename(pdf_path)}",
        json_data=json_response
    )

from services.legal_service import check_constitutional_validity

@router.post("/draft/legal_review")
def legal_review(gr_json: dict):
    review = check_constitutional_validity(gr_json)
    
    # Store the legal review in the RAG vector DB
    try:
        fields = gr_json.get("template_fields", {})
        gr_number = fields.get("gr_number", "UNKNOWN_GR")
        subject = fields.get("subject", "Unknown Subject")
        
        doc_text = f"Legal Review for GR {gr_number} on subject: {subject}. Is Valid: {review.get('is_valid')}. Analysis: {review.get('analysis')}. Recommendation: {review.get('recommendation')}"
        
        chunk = GRChunk(
            gr_no=string_to_int(f"{gr_number}_LEGAL_REVIEW"),
            department=fields.get("department", "Legal"),
            source_file=f"Legal_Review_{gr_number}.txt",
            language="en",
            chunk_id=2, # Use chunk 2 for legal review
            text=doc_text
        )
        embedding = get_embedding(doc_text)
        upload_chunks([chunk], [embedding])
    except Exception as e:
        print(f"Error adding legal review to Qdrant RAG: {e}")
        
    return review

@router.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join("./data/output", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@router.get("/rag/stats")
def get_rag_stats():
    from rag.qdrant_db import client
    from config import settings
    try:
        info = client.get_collection(settings.COLLECTION_NAME)
        return {
            "status": "success",
            "collection_name": settings.COLLECTION_NAME,
            "total_points_ingested": info.points_count
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

from models.schemas import FAQRequest
from services.llm_service import answer_faq

@router.post("/faq/ask")
def ask_faq(request: FAQRequest):
    try:
        answer = answer_faq(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

