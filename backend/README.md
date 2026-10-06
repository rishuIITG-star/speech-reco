# Inter IIT Meeting Assistant (Backend)

## Setup on Windows
1. Install Python 3.11+.
2. Install ffmpeg and ensure it is in your system PATH.
3. Install dependencies:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your keys (e.g. GEMINI_API_KEY).
5. Ensure Ollama is installed and running with the `qwen2.5:7b-instruct` model pulled:
   ```cmd
   ollama pull qwen2.5:7b-instruct
   ```

## Running the API
```cmd
venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Running Tests
```cmd
venv\Scripts\pytest tests/
```
