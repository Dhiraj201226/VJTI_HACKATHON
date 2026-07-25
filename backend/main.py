from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(title="MAHA-GR ALIGN API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to MAHA-GR ALIGN API"}
