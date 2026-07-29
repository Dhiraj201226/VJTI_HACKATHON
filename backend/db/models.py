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
    created_at = Column(DateTime, default=datetime.utcnow)
