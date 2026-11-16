from pathlib import Path

from app.services.audio_service import extract_audio
from app.services.transcription_service import transcribe_audio
from app.services.chunking_service import create_chunks
from app.services.embedding_service import create_embeddings
from app.services.vector_service import store_chunks
from app.services.status_service import set_status


# ==========================================
# DIRECTORIES
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

UPLOAD_DIR = PROJECT_ROOT / "uploads"
AUDIO_DIR = PROJECT_ROOT / "audio"
TRANSCRIPT_DIR = PROJECT_ROOT / "transcripts"
CHUNKS_DIR = PROJECT_ROOT / "chunks"


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# PROCESS VIDEO
# ==========================================

def process_video(video_id: str, video_path: str):

    try:

        print("\n")
        print("===================================")
        print("VIDMIND-AI VIDEO PROCESSING")
        print("===================================")
        print("Video ID:", video_id)
        print("Video:", video_path)
        print()


        # ==================================
        # STEP 1 — VIDEO UPLOADED
        # ==================================

        set_status(
            video_id,
            "uploaded",
            10,
            "Video uploaded successfully."
        )

        print("[10%] Video uploaded.")


        # ==================================
        # STEP 2 — EXTRACT AUDIO
        # ==================================

        set_status(
            video_id,
            "extracting_audio",
            20,
            "Extracting audio from video..."
        )

        audio_path = AUDIO_DIR / f"{video_id}.wav"

        extract_audio(
            video_path,
            str(audio_path)
        )

        set_status(
            video_id,
            "audio_extracted",
            35,
            "Audio extraction completed."
        )

        print("[35%] Audio extraction completed.")


        # ==================================
        # STEP 3 — TRANSCRIPTION
        # ==================================

        set_status(
            video_id,
            "transcribing",
            40,
            "Whisper is transcribing your video..."
        )

        transcript_path = (
            TRANSCRIPT_DIR /
            f"{video_id}.json"
        )

        def update_transcription_progress(
            progress,
            message
        ):
            set_status(
                video_id,
                "transcribing",
                progress,
                message
            )

        transcribe_audio(
            str(audio_path),
            str(transcript_path),
            progress_callback=update_transcription_progress
        )

        set_status(
            video_id,
            "transcribed",
            60,
            "Video transcription completed."
        )

        print("[60%] Transcription completed.")


        # ==================================
        # STEP 4 — CREATE CHUNKS
        # ==================================

        set_status(
            video_id,
            "chunking",
            65,
            "Creating searchable transcript chunks..."
        )

        chunk_data = create_chunks(
            str(transcript_path)
        )

        chunks = chunk_data["chunks"]

        if not chunks:
            raise ValueError(
                "No transcript chunks were generated."
            )

        # Save chunks for debugging / future use
        chunk_path = (
            CHUNKS_DIR /
            f"{video_id}.json"
        )

        import json

        with chunk_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                chunk_data,
                file,
                ensure_ascii=False,
                indent=4
            )

        print(
            f"[65%] Created {len(chunks)} chunks."
        )

        set_status(
            video_id,
            "chunked",
            70,
            f"Created {len(chunks)} transcript chunks."
        )


        # ==================================
        # STEP 5 — CREATE EMBEDDINGS
        # ==================================

        set_status(
            video_id,
            "embedding",
            75,
            "Creating embeddings for transcript chunks..."
        )

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = create_embeddings(
            texts
        )

        if embeddings is None:
            raise ValueError(
                "Embedding generation returned no data."
            )

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Number of embeddings does not "
                "match number of chunks."
            )

        print(
            f"[85%] Created {len(embeddings)} embeddings."
        )

        set_status(
            video_id,
            "embedded",
            85,
            f"Created {len(embeddings)} embeddings."
        )


        # ==================================
        # STEP 6 — STORE IN CHROMADB
        # ==================================

        set_status(
            video_id,
            "storing_vectors",
            90,
            "Storing video knowledge in vector database..."
        )

        collection_count = store_chunks(
            video_id,
            chunks,
            embeddings
        )

        print(
            f"[95%] Stored {collection_count} chunks "
            f"in ChromaDB."
        )

        set_status(
            video_id,
            "vector_stored",
            95,
            "Video knowledge stored successfully."
        )


        # ==================================
        # STEP 7 — READY
        # ==================================

        set_status(
            video_id,
            "completed",
            100,
            "Video is ready. You can now ask questions."
        )

        print()
        print("===================================")
        print("VIDEO PROCESSING COMPLETED")
        print("===================================")
        print("Video ID:", video_id)
        print("Chunks:", len(chunks))
        print("Embeddings:", len(embeddings))
        print("ChromaDB entries:", collection_count)
        print("Status: READY")
        print("===================================")
        print()


    except Exception as e:

        print()
        print("===================================")
        print("VIDEO PROCESSING FAILED")
        print("===================================")
        print("Video ID:", video_id)
        print("Error:", str(e))
        print("===================================")
        print()

        set_status(
            video_id,
            "failed",
            0,
            f"Processing failed: {str(e)}"
        )