call .venv\Scripts\activate
python -m uvicorn api:app --reload --host 0.0.0.0 --port 60001
pause