from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class GeneratedGR(Base):
    __tablename__ = "generated_grs"

    id = Column(Integer, primary_key=True, index=True)
    gr_number = Column(String, index=True)
    department = Column(String, index=True)
    subject = Column(String)
    date = Column(String)
    docx_path = Column(String)
    pdf_path = Column(String)
    status = Column(String, default="PENDING_DS_REVIEW")
    sha256_hash = Column(String, nullable=True)
    desk_officer_notes = Column(String, nullable=True)
    deputy_secy_notes = Column(String, nullable=True)
    secy_notes = Column(String, nullable=True)
    draft_json = Column(String, nullable=True)
    current_hash = Column(String, nullable=True)
    desk_officer_hash = Column(String, nullable=True)
    deputy_secy_hash = Column(String, nullable=True)
    priority = Column(String, default="Standard")
    created_at = Column(DateTime, default=datetime.utcnow)
