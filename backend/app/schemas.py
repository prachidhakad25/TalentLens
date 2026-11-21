from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class ProfileIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    education: str = ""
    degree: str = ""
    college: str = ""
    graduation_year: Optional[int] = None
    skills: list[str] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    certifications: list[dict] = Field(default_factory=list)
    experience: list[dict] = Field(default_factory=list)
    resume_skills: list[str] = Field(default_factory=list)
    github_url: str = ""
    github_languages: list[str] = Field(default_factory=list)
    github_repos: list[dict] = Field(default_factory=list)
    preferred_roles: list[str] = Field(default_factory=list)
    preferred_location: str = ""
    remote_preference: bool = True
    experience_years: float = Field(default=0, ge=0, le=50)
    bio: str = ""

class RecruiterProfileIn(BaseModel):
    company_name: str = ""
    website: str = ""
    industry: str = ""
    company_size: str = ""
    about: str = ""

class JobIn(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    company: str = Field(min_length=2, max_length=180)
    description: str = ""
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    degree: str = ""
    experience_min: float = Field(default=0, ge=0, le=50)
    location: str = "Remote"
    remote: bool = True
    work_mode: str = "Remote"
    job_type: str = "Internship"

class ApplicationStatusIn(BaseModel):
    status: str
