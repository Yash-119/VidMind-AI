from pathlib import Path

from app.services.chunking_service import save_chunks


VIDEO_ID = "5327e520-5e95-4de1-a1c2-99de9ce924f1"


PROJECT_ROOT = Path(__file__).resolve().parent

TRANSCRIPT_PATH = (
    PROJECT_ROOT /
    "transcripts" /
    f"{VIDEO_ID}.json"
)

CHUNK_PATH = (
    PROJECT_ROOT /
    "transcripts" /
    f"{VIDEO_ID}_chunks.json"
)


print("Starting transcript chunking...")

save_chunks(
    str(TRANSCRIPT_PATH),
    str(CHUNK_PATH)
)

print()
print("==============================")
print("CHUNKING TEST SUCCESSFUL")
print("==============================")