from pathlib import Path
import json

from faster_whisper import WhisperModel


# ==========================================
# WHISPER CONFIGURATION
# ==========================================

MODEL_SIZE = "base"

# Keep Whisper model on D: drive
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# LOAD WHISPER MODEL
# ==========================================

print("Loading Whisper model...")

model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8",
    download_root=str(MODEL_DIR)
)

print("Whisper model loaded successfully.")


# ==========================================
# TRANSCRIBE AUDIO
# ==========================================

def transcribe_audio(
    audio_path: str,
    transcript_path: str,
    progress_callback=None
) -> str:

    audio = Path(audio_path)
    output = Path(transcript_path)

    # --------------------------------------
    # Check audio file
    # --------------------------------------

    if not audio.exists():
        raise FileNotFoundError(
            f"Audio file not found: {audio}"
        )

    # --------------------------------------
    # Create output directory
    # --------------------------------------

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Starting transcription...")

    # --------------------------------------
    # Start Whisper
    # --------------------------------------

    segments, info = model.transcribe(
        str(audio),
        beam_size=5,
        vad_filter=True
    )

    # --------------------------------------
    # Get total audio duration
    # --------------------------------------

    total_duration = info.duration

    if not total_duration or total_duration <= 0:
        total_duration = 1

    print(
        f"Audio duration: {total_duration:.2f} seconds"
    )

    transcript_segments = []
    full_text = []

    last_progress = 50

    # ======================================
    # PROCESS WHISPER SEGMENTS
    # ======================================

    for segment in segments:

        text = segment.text.strip()

        # ----------------------------------
        # Save segment
        # ----------------------------------

        transcript_segments.append({
            "start": segment.start,
            "end": segment.end,
            "text": text
        })

        full_text.append(text)

        # ----------------------------------
        # Calculate transcription progress
        # ----------------------------------

        processed_time = segment.end

        progress_ratio = (
            processed_time / total_duration
        )

        # Whisper stage:
        # 50% -> 95%
        progress = 50 + (
            progress_ratio * 45
        )

        progress = int(
            min(
                max(progress, 50),
                95
            )
        )

        # ----------------------------------
        # Avoid sending same progress again
        # ----------------------------------

        if progress != last_progress:

            last_progress = progress

            print(
                f"Whisper progress: {progress}% "
                f"({processed_time:.1f}s / "
                f"{total_duration:.1f}s)"
            )

            # --------------------------------
            # Send progress to backend
            # --------------------------------

            if progress_callback:

                progress_callback(
                    progress,
                    (
                        "Whisper is transcribing "
                        f"your video... {progress}%"
                    )
                )

    # ======================================
    # TRANSCRIPTION FINISHED
    # ======================================

    if progress_callback:

        progress_callback(
            96,
            "Whisper transcription completed. Saving transcript..."
        )

    # ======================================
    # CREATE TRANSCRIPT JSON
    # ======================================

    transcript_data = {

        "language": info.language,

        "language_probability":
            info.language_probability,

        "duration":
            total_duration,

        "text":
            " ".join(full_text),

        "segments":
            transcript_segments
    }

    # ======================================
    # SAVE JSON
    # ======================================

    with output.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            transcript_data,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("Transcription completed.")

    # ======================================
    # FINAL PROGRESS
    # ======================================

    if progress_callback:

        progress_callback(
            100,
            "Transcription completed successfully."
        )

    return str(output)
