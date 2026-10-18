import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
# Fallback to backend/.env if running from workspace root
load_dotenv(Path(__file__).resolve().parent / ".env")

app = FastAPI(title="Real Estate AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import price
app.include_router(price.router)



@app.get("/api/health")
def health():
    return {"status": "ok", "gemini_key_loaded": bool(os.getenv("GEMINI_API_KEY"))}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
