import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
load_dotenv(Path(__file__).resolve().parent / ".env")

from services.database import init_db
from routers import deals, describe, marketplace, price

init_db()

app = FastAPI(title="Real Estate AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(price.router)
app.include_router(marketplace.router)
app.include_router(deals.router)
app.include_router(describe.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "gemini_key_loaded": bool(os.getenv("GEMINI_API_KEY"))}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
