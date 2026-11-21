import os
from io import BytesIO
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from pypdf import PdfReader
from .database import Base, engine, get_db
from .models import User, StudentProfile, RecruiterProfile, Job, Application
from .schemas import RegisterIn, LoginIn, ProfileIn, RecruiterProfileIn, JobIn, ApplicationStatusIn
from .security import hash_password, verify_password, create_access_token, get_current_user, require_role
from .matching import calculate_match, rank_candidates
from .integrations import fetch_github_profile, openai_profile_insight

load_dotenv()
Base.metadata.create_all(bind=engine)
app = FastAPI(title="TalentLens API", version="3.0.0", description="Python-first, explainable talent discovery platform")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def user_out(user):
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}

def profile_out(profile):
    if not profile:
        return {}
    keys = ["education", "degree", "college", "graduation_year", "skills", "projects", "certifications",
            "experience", "resume_skills", "github_url", "github_languages", "github_repos",
            "preferred_roles", "preferred_location", "remote_preference", "experience_years", "bio"]
    return {k: getattr(profile, k) for k in keys}

def recruiter_profile_out(profile):
    if not profile:
        return {}
    return {k: getattr(profile, k) for k in ["company_name", "website", "industry", "company_size", "about"]}

def job_out(job):
    return {"id": job.id, "title": job.title, "company": job.company, "description": job.description,
            "required_skills": job.required_skills or [], "preferred_skills": job.preferred_skills or [],
            "degree": job.degree, "experience_min": job.experience_min, "location": job.location,
            "remote": job.remote, "work_mode": job.work_mode, "job_type": job.job_type,
            "is_active": job.is_active, "recruiter_id": job.recruiter_id}

@app.get("/")
def root():
    return {"name": "TalentLens API", "status": "running", "version": "3.0.0", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/auth/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    role = payload.role.lower().strip()
    if role not in {"student", "recruiter"}:
        raise HTTPException(400, "Role must be student or recruiter")
    email = str(payload.email).lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists")
    user = User(name=payload.name.strip(), email=email, password_hash=hash_password(payload.password), role=role)
    db.add(user)
    db.flush()
    if role == "student":
        db.add(StudentProfile(user_id=user.id))
    else:
        db.add(RecruiterProfile(user_id=user.id))
    db.commit()
    db.refresh(user)
    return {"token": create_access_token(user), "user": user_out(user)}

@app.post("/api/auth/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return {"token": create_access_token(user), "user": user_out(user)}

@app.get("/api/me")
def me(user: User = Depends(get_current_user)):
    return user_out(user)

@app.get("/api/profile")
def get_profile(user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
    return {"user": user_out(user), "profile": profile_out(profile)}

@app.put("/api/profile")
def update_profile(payload: ProfileIn, user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
    if not profile:
        profile = StudentProfile(user_id=user.id)
        db.add(profile)
    for key, value in payload.model_dump().items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return {"message": "Profile saved", "profile": profile_out(profile)}

@app.post("/api/github/sync")
def github_sync(user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
    if not profile or not profile.github_url:
        raise HTTPException(400, "Save your GitHub profile URL before syncing.")
    data = fetch_github_profile(profile.github_url)
    profile.github_languages = data["languages"]
    profile.github_repos = data["repos"]
    db.commit()
    return data

@app.post("/api/ai/profile-insight")
def profile_insight(user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
    payload = profile_out(profile)
    payload["name"] = user.name
    return {"insight": openai_profile_insight(payload)}

@app.get("/api/company")
def get_company(user: User = Depends(require_role("recruiter")), db: Session = Depends(get_db)):
    company = db.scalar(select(RecruiterProfile).where(RecruiterProfile.user_id == user.id))
    return {"company": recruiter_profile_out(company)}

@app.put("/api/company")
def update_company(payload: RecruiterProfileIn, user: User = Depends(require_role("recruiter")), db: Session = Depends(get_db)):
    company = db.scalar(select(RecruiterProfile).where(RecruiterProfile.user_id == user.id))
    if not company:
        company = RecruiterProfile(user_id=user.id)
        db.add(company)
    for key, value in payload.model_dump().items():
        setattr(company, key, value)
    db.commit()
    return {"message": "Company profile saved", "company": recruiter_profile_out(company)}

@app.get("/api/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.scalars(select(Job).where(Job.is_active.is_(True)).order_by(Job.id.desc())).all()
    return [job_out(j) for j in jobs]

@app.post("/api/jobs")
def create_job(payload: JobIn, user: User = Depends(require_role("recruiter")), db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["company"] = data["company"].strip()
    job = Job(recruiter_id=user.id, **data)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job_out(job)

@app.get("/api/jobs/mine")
def my_jobs(user: User = Depends(require_role("recruiter")), db: Session = Depends(get_db)):
    jobs = db.scalars(select(Job).where(Job.recruiter_id == user.id).order_by(Job.id.desc())).all()
    return [job_out(j) for j in jobs]

@app.patch("/api/jobs/{job_id}/toggle")
def toggle_job(job_id: int, user: User = Depends(require_role("recruiter")), db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job or job.recruiter_id != user.id:
        raise HTTPException(404, "Job not found")
    job.is_active = not job.is_active
    db.commit()
    return {"message": "Job updated", "is_active": job.is_active}

@app.post("/api/jobs/{job_id}/apply")
def apply(job_id: int, user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job or not job.is_active:
        raise HTTPException(404, "Job not found")
    existing = db.scalar(select(Application).where(Application.job_id == job_id, Application.student_id == user.id))
    if existing:
        raise HTTPException(409, "You have already applied to this job")
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
    score = calculate_match(profile_out(profile), job_out(job))["match_score"]
    application = Application(job_id=job_id, student_id=user.id, match_score=score)
    db.add(application)
    db.commit()
    return {"message": "Application submitted", "match_score": score}

@app.get("/api/applications")
def applications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == "student":
        rows = db.scalars(select(Application).where(Application.student_id == user.id).order_by(Application.id.desc())).all()
    else:
        owned_ids = select(Job.id).where(Job.recruiter_id == user.id)
        rows = db.scalars(select(Application).where(Application.job_id.in_(owned_ids)).order_by(Application.id.desc())).all()
    output = []
    for row in rows:
        job, student = db.get(Job, row.job_id), db.get(User, row.student_id)
        output.append({"id": row.id, "job": job_out(job) if job else None,
                       "student": user_out(student) if student else None,
                       "status": row.status, "match_score": row.match_score})
    return output

@app.patch("/api/applications/{application_id}/status")
def update_application_status(application_id: int, payload: ApplicationStatusIn,
                              user: User = Depends(require_role("recruiter")), db: Session = Depends(get_db)):
    allowed = {"applied", "shortlisted", "interview", "rejected", "hired"}
    if payload.status not in allowed:
        raise HTTPException(400, f"Status must be one of: {', '.join(sorted(allowed))}")
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(404, "Application not found")
    job = db.get(Job, application.job_id)
    if not job or job.recruiter_id != user.id:
        raise HTTPException(403, "You cannot update this application")
    application.status = payload.status
    db.commit()
    return {"message": "Application status updated", "status": application.status}

@app.get("/api/candidates")
def candidates(job_id: int | None = None, user: User = Depends(require_role("recruiter")), db: Session = Depends(get_db)):
    profiles = db.scalars(select(StudentProfile)).all()
    students = []
    for profile in profiles:
        student_user = db.get(User, profile.user_id)
        if student_user:
            item = profile_out(profile)
            item.update({"id": student_user.id, "name": student_user.name, "email": student_user.email})
            students.append(item)
    if job_id is None:
        return students
    job = db.get(Job, job_id)
    if not job or job.recruiter_id != user.id:
        raise HTTPException(404, "Job not found")
    return rank_candidates(students, job_out(job))

@app.post("/api/resume/analyze")
async def analyze_resume(file: UploadFile = File(...), user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF resume")
    raw = await file.read()
    if len(raw) > 8 * 1024 * 1024:
        raise HTTPException(413, "Resume must be 8 MB or smaller")
    try:
        reader = PdfReader(BytesIO(raw))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        raise HTTPException(400, "Could not read this PDF. Try exporting it again.")
    vocabulary = ["python", "sql", "pandas", "numpy", "power bi", "tableau", "excel", "machine learning",
                  "scikit-learn", "tensorflow", "pytorch", "streamlit", "fastapi", "data analysis",
                  "data science", "statistics", "plotly", "scikit learn", "postgresql", "mongodb",
                  "javascript", "react", "node.js", "git", "docker", "aws", "azure"]
    lower = text.lower()
    found = sorted({skill for skill in vocabulary if skill in lower})
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
    if profile:
        profile.resume_skills = found
        db.commit()
    return {"filename": file.filename, "pages": len(reader.pages), "extracted_skills": found,
            "text_preview": text[:1800], "message": "Resume skills saved as profile evidence. Review them before relying on the match."}
