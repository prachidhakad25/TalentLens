"""Explainable, deterministic talent matching. This is a fit score, not hiring probability."""
import re

SKILL_ALIASES = {
    "python3": "python", "mysql": "sql", "postgresql": "sql",
    "postgres": "sql", "ml": "machine learning", "js": "javascript",
    "powerbi": "power bi", "scikit learn": "scikit-learn",
    "pytorch": "pytorch", "ms excel": "excel",
}

WEIGHTS = {
    "skills": 0.35,
    "projects": 0.25,
    "github": 0.15,
    "education": 0.10,
    "experience": 0.10,
    "location": 0.05,
}

def normalize(text):
    if not text:
        return ""
    value = re.sub(r"[^a-z0-9+#.\s]", " ", str(text).lower())
    return re.sub(r"\s+", " ", value).strip()

def normalize_skill(skill):
    value = normalize(skill)
    return SKILL_ALIASES.get(value, value)

def as_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [x.strip() for x in value.split(",") if x.strip()]
    return list(value)

def calculate_match(student, job):
    skills = {normalize_skill(x) for x in as_list(student.get("skills"))}
    skills |= {normalize_skill(x) for x in as_list(student.get("resume_skills"))}
    projects = as_list(student.get("projects"))
    project_skills, relevant_projects = set(), []
    required = {normalize_skill(x) for x in as_list(job.get("required_skills"))}
    preferred = {normalize_skill(x) for x in as_list(job.get("preferred_skills"))}

    for project in projects:
        if isinstance(project, dict):
            tech = {normalize_skill(x) for x in as_list(project.get("technologies", []))}
            project_skills |= tech
            if tech & (required | preferred):
                relevant_projects.append(project.get("title", "Project"))
        elif isinstance(project, str):
            tech = {normalize_skill(x) for x in re.findall(r"[A-Za-z][A-Za-z0-9+#. ]{1,24}", project)}
            project_skills |= tech
            if tech & (required | preferred):
                relevant_projects.append(project[:80])

    evidence_skills = skills | project_skills
    matched = evidence_skills & required
    missing = required - evidence_skills
    skill_score = (len(matched) / len(required) * 100) if required else 0.0
    project_score = (len(project_skills & required) / len(required) * 100) if required else 0.0

    github = student.get("github_profile") or {}
    github_languages = as_list(github.get("languages", [])) or as_list(student.get("github_languages", []))
    github_skills = {normalize_skill(x) for x in github_languages}
    github_score = (len(github_skills & required) / len(required) * 100) if required else 0.0

    degree_required = normalize(job.get("degree", ""))
    degree_student = normalize(student.get("degree", "") or student.get("education", ""))
    education_score = 100.0 if not degree_required else (
        100.0 if degree_required in degree_student else
        80.0 if degree_student and degree_student in degree_required else 0.0
    )

    required_exp = float(job.get("experience_min") or 0)
    actual_exp = float(student.get("experience_years") or 0)
    experience_score = 100.0 if required_exp <= 0 else min(100.0, actual_exp / required_exp * 100)

    preferred_location = normalize(student.get("preferred_location", ""))
    job_location = normalize(job.get("location", ""))
    remote_student, remote_job = bool(student.get("remote_preference", True)), bool(job.get("remote", False))
    if remote_job and remote_student:
        location_score = 100.0
    elif not preferred_location:
        location_score = 50.0
    elif preferred_location in job_location or job_location in preferred_location:
        location_score = 100.0
    else:
        location_score = 30.0

    preferred_roles = [normalize(x) for x in as_list(student.get("preferred_roles"))]
    title = normalize(job.get("title", ""))
    role_score = 50.0 if not preferred_roles else (
        100.0 if any(x and x in title for x in preferred_roles) else
        70.0 if any(set(x.split()) & set(title.split()) for x in preferred_roles) else 30.0
    )

    score = (
        skill_score * WEIGHTS["skills"] +
        project_score * WEIGHTS["projects"] +
        github_score * WEIGHTS["github"] +
        education_score * WEIGHTS["education"] +
        experience_score * WEIGHTS["experience"] +
        location_score * WEIGHTS["location"]
    )
    # Role preference is shown separately, preserving the original MVP's weighting.
    score = round(min(100.0, score), 1)
    components = {
        "Skills": round(skill_score, 1),
        "Project evidence": round(project_score, 1),
        "GitHub languages": round(github_score, 1),
        "Education": round(education_score, 1),
        "Experience": round(experience_score, 1),
        "Location / remote": round(location_score, 1),
    }
    return {
        "match_score": score,
        "skill_score": round(skill_score, 1),
        "project_score": round(project_score, 1),
        "github_score": round(github_score, 1),
        "education_score": round(education_score, 1),
        "experience_score": round(experience_score, 1),
        "role_score": round(role_score, 1),
        "location_score": round(location_score, 1),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "relevant_projects": relevant_projects,
        "components": components,
        "weights": {k: round(v * 100) for k, v in WEIGHTS.items()},
        "explanation": {
            "skills": f"{len(matched)} of {len(required)} required skills evidenced.",
            "projects": f"{len(relevant_projects)} project(s) contain related technology evidence.",
            "github": f"{len(github_skills & required)} required skill(s) appear in public GitHub language data.",
            "education": f"Education alignment: {education_score:.0f}%.",
            "experience": f"Recorded experience: {actual_exp:g} year(s); role asks for {required_exp:g}.",
            "role": f"Preferred-role alignment: {role_score:.0f}% (displayed separately, not included in the legacy weighted total).",
            "location": f"Location/work-mode alignment: {location_score:.0f}%.",
        },
        "score_note": "An evidence-based profile-to-role fit indicator, not a probability of being hired. Human review remains essential.",
    }

def rank_candidates(students_list, job):
    results = []
    for student in students_list:
        result = calculate_match(student, job)
        result["student"] = student
        results.append(result)
    results.sort(key=lambda item: item["match_score"], reverse=True)
    for rank, result in enumerate(results, start=1):
        result["rank"] = rank
    return results
