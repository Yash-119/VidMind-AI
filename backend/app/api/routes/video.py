from pathlib import Path
import shutil
import uuid

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks
)
from pydantic import BaseModel, Field
from typing import Literal

from app.services.processing_service import process_video
from app.services.status_service import (
    set_status,
    get_status
)
from app.services.search_service import search_video
from app.services.llm_service import (
    generate_answer,
    evaluate_answer_accuracy
)
from app.services.quiz_service import (
    generate_quiz,
    submit_quiz
)

class YouTubeURLRequest(BaseModel):
    url: str = Field(..., min_length=10)

router = APIRouter()


# ==========================================
# DIRECTORIES
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

UPLOAD_DIR = PROJECT_ROOT / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# SUPPORTED FORMATS
# ==========================================

ALLOWED_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".webm"
}


# ==========================================
# ASK REQUEST
# ==========================================

class AskRequest(BaseModel):
    question: str
class QuizGenerateRequest(BaseModel):
    question_count: int = Field(default=15, ge=1, le=100)
    difficulty: Literal[
        "Easy",
        "Normal",
        "Difficult",
        "Extreme"
    ] = "Easy"


class QuizSubmitRequest(BaseModel):
    answers: dict[str, str] = Field(default_factory=dict)


# ==========================================
# UPLOAD VIDEO
# ==========================================

@router.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported video format: "
                f"{extension}"
            )
        )

    video_id = str(
        uuid.uuid4()
    )

    filename = (
        f"{video_id}{extension}"
    )

    file_path = (
        UPLOAD_DIR /
        filename
    )

    try:

        with file_path.open("wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save video: {str(e)}"
            )
        )

    background_tasks.add_task(
        process_video,
        video_id,
        str(file_path)
    )

    return {
        "success": True,
        "message": (
            "Video uploaded successfully. "
            "Processing started."
        ),
        "video_id": video_id,
        "filename": filename,
        "path": str(file_path),
        "status": "processing"
    }


# ==========================================
# VIDEO STATUS
# ==========================================

@router.get("/{video_id}/status")
async def video_status(video_id: str):

    return get_status(
        video_id
    )


# ==========================================
# ASK QUESTION ABOUT VIDEO
# ==========================================

@router.post("/{video_id}/ask")
async def ask_video(
    video_id: str,
    request: AskRequest
):

    question = (
        request.question or ""
    ).strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # --------------------------------------
    # Verify video is ready
    # --------------------------------------

    status_data = get_status(
        video_id
    )

    if not status_data:

        raise HTTPException(
            status_code=404,
            detail="Video not found."
        )

    if status_data.get("status") != "completed":

        raise HTTPException(
            status_code=400,
            detail=(
                "This video is not ready yet. "
                "Please wait for processing to complete."
            )
        )

    # --------------------------------------
    # Search this video's vector database
    # --------------------------------------

    try:

        search_results = search_video(
            video_id,
            question,
            top_k=5
        )

    except Exception as e:

        print(
            "Video search error:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to search the video's "
                f"knowledge base: {str(e)}"
            )
        )

    # --------------------------------------
    # Generate grounded Gemini answer
    # --------------------------------------

    try:

        answer = generate_answer(
            question,
            search_results
        )

    except Exception as e:

        print(
            "Gemini error:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Gemini could not generate an answer: {str(e)}"
            )
        )

    # --------------------------------------
    # Evaluate answer accuracy
    # --------------------------------------

    accuracy_result = evaluate_answer_accuracy(
        question,
        answer,
        search_results
    )

    # --------------------------------------
    # Return answer + sources
    # --------------------------------------

    sources = []

    for result in search_results:

        sources.append({
            "chunk_id": result.get(
                "chunk_id"
            ),
            "start": result.get(
                "start",
                0
            ),
            "end": result.get(
                "end",
                0
            ),
            "similarity": result.get(
                "similarity",
                0
            ),
            "text": result.get(
                "text",
                ""
            )
        })

        return {
        "success": True,
        "video_id": video_id,
        "question": question,
        "answer": answer,
        "accuracy": accuracy_result.get(
            "accuracy"
        ),
        "accuracy_reason": accuracy_result.get(
            "reason",
            ""
        ),
        "sources": sources
    }


# ==========================================
# GENERATE VIDEO QUIZ
# ==========================================

@router.post("/{video_id}/quiz/generate")
async def create_video_quiz(
    video_id: str,
    request: QuizGenerateRequest
):
    status_data = get_status(video_id)

    if not status_data:
        raise HTTPException(
            status_code=404,
            detail="Video not found."
        )

    if status_data.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail="Video processing is not complete."
        )

    try:
        result = generate_quiz(
            video_id=video_id,
            question_count=request.question_count,
            difficulty=request.difficulty
        )

        return {
            "success": True,
            **result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        print("Quiz generation error:", str(e))

        raise HTTPException(
            status_code=500,
            detail="Unable to generate the quiz. Please try again."
        )


# ==========================================
# SUBMIT VIDEO QUIZ
# ==========================================

@router.post("/{video_id}/quiz/{quiz_id}/submit")
async def submit_video_quiz(
    video_id: str,
    quiz_id: str,
    request: QuizSubmitRequest
):
    try:
        result = submit_quiz(
            video_id=video_id,
            quiz_id=quiz_id,
            answers=request.answers
        )

        return {
            "success": True,
            **result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        print("Quiz submission error:", str(e))

        raise HTTPException(
            status_code=500,
            detail="Unable to submit the quiz."
        )


def process_youtube_video(video_id: str, url: str):
    import yt_dlp

    try:
        set_status(
            video_id,
            "downloading",
            5,
            "Connecting to YouTube..."
        )

        output_template = str(
            UPLOAD_DIR / f"{video_id}.%(ext)s"
        )

        last_progress = [-1]

        def download_progress_hook(data):
            if data.get("status") == "downloading":
                total = (
                    data.get("total_bytes")
                    or data.get("total_bytes_estimate")
                )
                downloaded = data.get("downloaded_bytes", 0)

                if total and total > 0:
                    percent = min(
                        100,
                        int(downloaded * 100 / total)
                    )

                    if percent != last_progress[0]:
                        last_progress[0] = percent

                        progress = 5 + int(percent * 0.05)

                        set_status(
                            video_id,
                            "downloading",
                            progress,
                            f"Downloading YouTube video: {percent}%"
                        )

            elif data.get("status") == "finished":
                set_status(
                    video_id,
                    "downloading",
                    10,
                    "Download complete. Preparing video..."
                )

        options = {
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "js_runtimes": {"deno": {}},
            "remote_components": ["ejs:github"],
            "progress_hooks": [download_progress_hook],
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = Path(ydl.prepare_filename(info))

        if not file_path.exists():
            candidates = list(
                UPLOAD_DIR.glob(f"{video_id}.*")
            )
            candidates = [
                path for path in candidates
                if path.is_file()
                and path.suffix.lower() not in {
                    ".part", ".ytdl"
                }
            ]

            if not candidates:
                raise FileNotFoundError(
                    "Downloaded video file was not found."
                )

            file_path = candidates[0]

        process_video(video_id, str(file_path))

    except Exception as exc:
        set_status(
            video_id,
            "failed",
            0,
            f"YouTube processing failed: {exc}"
        )

@router.post("/youtube")
def upload_youtube_video(
    request: YouTubeURLRequest,
    background_tasks: BackgroundTasks
):
    url = request.url.strip()

    if not (
        "youtube.com/" in url
        or "youtu.be/" in url
    ):
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid YouTube URL."
        )

    video_id = str(uuid.uuid4())

    set_status(
        video_id,
        "downloading",
        5,
        "Preparing YouTube download..."
    )

    background_tasks.add_task(
        process_youtube_video,
        video_id,
        url
    )

    return {
        "video_id": video_id,
        "status": "downloading",
        "message": "YouTube video download started."
    }