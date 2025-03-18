import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend.model import Base, Job, Resume

DATABASE_URL = "postgresql://postgres:secret@localhost:5432/job_recommendation"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def create_job_in_db(description: str, location: str):
    db = SessionLocal()
    new_job = Job(description=description, location=location)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    db.close()
    return {"id": new_job.id, "description": new_job.description, "location": new_job.location}

def save_resume_in_db(job_id: int, filename: str):
    db = SessionLocal()
    new_resume = Resume(job_id=job_id, file_path=filename)
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    db.close()
    
    return {
        "message": "Resume uploaded successfully",
        "job_id": job_id,
        "file_path": f"/resumes/{filename}"
    }

def get_resume_by_id(resume_id: int):
    db = SessionLocal()
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    db.close()
    return resume

def get_job_by_id(job_id: int):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    return job
