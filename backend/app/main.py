from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.video import router as video_router


app = FastAPI(
    title="VidMind AI",
    description="Intelligent Video Knowledge Search and Question Answering System",
    version="1.0.0"
)


# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Video routes
app.include_router(
    video_router,
    prefix="/api/videos",
    tags=["Videos"]
)


@app.get("/")
def root():
    return {
        "message": "VidMind AI Backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }