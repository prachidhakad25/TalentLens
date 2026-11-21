import os
import re
import requests
from fastapi import HTTPException

def github_username(profile_url: str) -> str:
    match = re.match(r"^https?://(?:www\.)?github\.com/([A-Za-z0-9-]+)/?$", (profile_url or "").strip())
    if not match:
        raise HTTPException(400, "Enter a valid public GitHub profile URL, e.g. https://github.com/octocat")
    return match.group(1)

def fetch_github_profile(profile_url: str):
    username = github_username(profile_url)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "TalentLens"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        user_resp = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=12)
        user_resp.raise_for_status()
        repos_resp = requests.get(f"https://api.github.com/users/{username}/repos", headers=headers, params={"per_page": 100, "sort": "updated"}, timeout=12)
        repos_resp.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(502, f"GitHub API request failed: {exc}")
    repos = [r for r in repos_resp.json() if not r.get("fork")]
    languages = sorted({r.get("language") for r in repos if r.get("language")})
    return {
        "username": username,
        "name": user_resp.json().get("name") or username,
        "public_repos": user_resp.json().get("public_repos", 0),
        "followers": user_resp.json().get("followers", 0),
        "languages": languages,
        "repos": [{"name": r.get("name"), "description": r.get("description"), "language": r.get("language"), "url": r.get("html_url"), "stars": r.get("stargazers_count", 0)} for r in repos[:20]],
        "profile_url": user_resp.json().get("html_url"),
    }

def openai_profile_insight(profile: dict):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(503, "AI narrative insights are optional. Add OPENAI_API_KEY to backend/.env to enable this feature.")
    prompt = (
        "You are a career coach. Give concise, evidence-grounded feedback based only on this student profile. "
        "Return: strengths, skill gaps, 3 next actions. Do not invent credentials or promise hiring outcomes. "
        f"Profile: {profile}"
    )
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"), "messages": [{"role": "user", "content": prompt}], "temperature": 0.3},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as exc:
        raise HTTPException(502, f"AI provider request failed: {exc}")
