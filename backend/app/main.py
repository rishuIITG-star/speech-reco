from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes, auth
from app.core.database import engine, Base
from app.ml.asr.transcribe import get_model as init_asr
from app.core.config import config
from app.core.worker import start_worker
from dotenv import load_dotenv

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inter IIT Meeting Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    refiner_full = f"{config.refiner.provider}/{config.refiner.model}"
    extractor_full = f"{config.extractor.provider}/{config.extractor.model}"
    if refiner_full == extractor_full:
        raise ValueError(f"CRITICAL: Refiner and Extractor must use different models. Both are set to {refiner_full}.")
        
    # Start background job worker
    start_worker()
    # Preload ASR model
    init_asr()
    
app.include_router(routes.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
