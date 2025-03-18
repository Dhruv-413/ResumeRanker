import os
from backend.extract_text import extract_text
from backend.scoring import evaluate_cv_quality, extract_experience_details, compute_similarity_bert, extract_location, compute_location_score
from fastapi import FastAPI, HTTPException, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import FileResponse
from backend.db import create_job_in_db, save_resume_in_db, get_resume_by_id, get_job_by_id
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.model import Base, Job, Resume

RESUME_FOLDER = os.path.join(os.getcwd(), "data")

DATABASE_URL = "postgresql://postgres:secret@localhost:5432/job_recommendation"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()

WEIGHTS = {"quality": 5, "experience": 50, "years": 10, "location": 10}

class JobRequest(BaseModel):
    description: str
    location: str

class ScoreRequest(BaseModel):
    resume_id: int

data_folder = os.path.join(os.getcwd(), "data")
os.makedirs(data_folder, exist_ok=True)

@app.post("/job")
def create_job(job: JobRequest):
    return create_job_in_db(job.description, job.location)

@app.post("/apply")
def upload_resume(job_id: int = Form(...), resume: UploadFile = Form(...)):
    if not resume:
        raise HTTPException(status_code=400, detail="Resume file is required")
    
    file_path = os.path.join(data_folder, resume.filename)
    with open(file_path, "wb") as f:
        f.write(resume.file.read())

    return save_resume_in_db(job_id, resume.filename)

@app.post("/calculate_score")
def calculate_score(request: ScoreRequest):
    resume = get_resume_by_id(request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job = get_job_by_id(resume.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not os.path.exists(resume.file_path):
        raise HTTPException(status_code=400, detail="Resume file not found on server")

    resume_text = extract_text(resume.file_path)
    quality_score = evaluate_cv_quality(resume_text)
    experience_details = extract_experience_details(resume_text)
    years_experience = experience_details["years_experience"]
    relevance_score = compute_similarity_bert(resume_text, job.description)
    candidate_location = extract_location(resume_text)
    location_score = compute_location_score(candidate_location, job.location)

    total_score = (
        (quality_score * WEIGHTS.get("quality", 0)) +
        (relevance_score * WEIGHTS.get("experience", 0)) +
        (years_experience * WEIGHTS.get("years", 0)) +
        (location_score * WEIGHTS.get("location", 0))
    ) / sum(WEIGHTS.values())

    return {
        "quality_score": quality_score,
        "relevance_score": relevance_score,
        "years_experience": years_experience,
        "location_score": location_score,
        "total_score": round(total_score, 2)
    }

@app.get("/resumes/{resume_id}")
def view_resume(resume_id: int):
    resume = get_resume_by_id(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    file_path = os.path.join(RESUME_FOLDER, resume.file_path)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Resume file not found on server")

    return FileResponse(file_path, media_type="application/pdf" if file_path.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
