@echo off
cd /d %~dp0
call .venv\Scripts\activate
streamlit run streamlit_app\app.py --server.port 8501
