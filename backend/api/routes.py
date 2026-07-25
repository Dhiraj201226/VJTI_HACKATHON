from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from models.schemas import DraftRequest, GenerateRequest, FinalDraftResponse, LLMDraftResponse
from services.rag_service import search_gr, add_documents
from services.conflict_service import detect_conflicts
from services.llm_service import generate_gr_json
from services.document_service import generate_documents
import os

router = APIRouter()

@router.post("/draft/initiate")
def initiate_draft(request: DraftRequest):
    objective = request.objective
    
    # 1. Retrieve chunks
    results = search_gr(objective, top_k=3)
    
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

@router.post("/draft/generate", response_model=FinalDraftResponse)
def generate_draft(request: GenerateRequest):
    # Re-retrieve or use passed context (simplified here to re-retrieve)
    results = search_gr(request.objective, top_k=3)
    
    # Generate JSON from LLM
    json_response = generate_gr_json(request.objective, results, request.officer_decisions)
    
    # Generate Documents
    docx_path, pdf_path = generate_documents(json_response)
    
    # Store generated GR in RAG
    fields = json_response.template_fields
    doc_text = f"Government Resolution regarding {fields.subject}. {' '.join(fields.body)} Dept: {fields.department}. Date: {fields.date}. GR: {fields.gr_number}"
    metadata = {
        "department": fields.department,
        "date": fields.date,
        "gr_number": fields.gr_number,
        "policy_area": fields.subject
    }
    try:
        add_documents([doc_text], [metadata], [fields.gr_number])
    except Exception as e:
        print(f"Error adding to RAG: {e}")
    
    return FinalDraftResponse(
        docx_url=f"/api/download/{os.path.basename(docx_path)}",
        pdf_url=f"/api/download/{os.path.basename(pdf_path)}",
        json_data=json_response
    )

@router.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join("./data/output", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")
