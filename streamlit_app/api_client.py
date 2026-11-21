import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("TALENTLENS_API_URL", "http://127.0.0.1:8000").rstrip("/")

def request(method, path, **kwargs):
    headers = dict(kwargs.pop("headers", {}))
    token = st.session_state.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.request(method, f"{BASE_URL}{path}", headers=headers, timeout=25, **kwargs)
    except requests.RequestException as exc:
        raise RuntimeError(f"Cannot reach TalentLens API at {BASE_URL}. Start FastAPI first. Details: {exc}")
    try:
        data = response.json()
    except ValueError:
        data = {"detail": response.text[:500]}
    if not response.ok:
        detail = data.get("detail", f"HTTP {response.status_code}") if isinstance(data, dict) else str(data)
        raise RuntimeError(str(detail))
    return data

def get(path): return request("GET", path)
def post(path, payload=None): return request("POST", path, json=payload or {})
def put(path, payload): return request("PUT", path, json=payload)
def patch(path, payload=None): return request("PATCH", path, json=payload or {})
