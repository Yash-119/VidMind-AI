from pathlib import Path
import json

from app.services.embedding_service import create_embeddings
from app.services.vector_service import store_chunks


# ==========================================
# VIDEO ID
# ==========================================

VIDEO_ID = "5327e520-5e95-4de1-a1c2-99de9ce924f1"


# ==========================================
# PATH
# ==========================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent

CHUNK_FILE = (
    PROJECT_ROOT /
    "transcripts" /
    f"{VIDEO_ID}_chunks.json"
)


# ==========================================
# LOAD CHUNKS
# ==========================================

print()
print("Loading transcript chunks...")

with CHUNK_FILE.open(
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


chunks = data["chunks"]


print(
    f"Loaded {len(chunks)} chunks."
)


# ==========================================
# EXTRACT TEXT
# ==========================================

texts = [
    chunk["text"]
    for chunk in chunks
]


# ==========================================
# CREATE EMBEDDINGS
# ==========================================

print()
print("Creating embeddings...")

embeddings = create_embeddings(
    texts
)


print(
    f"Created {len(embeddings)} embeddings."
)


# ==========================================
# STORE IN CHROMA
# ==========================================

print()
print("Storing embeddings in ChromaDB...")


count = store_chunks(
    VIDEO_ID,
    chunks,
    embeddings
)


# ==========================================
# SUCCESS
# ==========================================

print()
print("==============================")
print("VECTOR DATABASE TEST SUCCESSFUL")
print("==============================")

print(
    f"Chunks stored: {count}"
)

print(
    "Database location:"
)

print(
    r"D:\VidMind-AI\vector_db"
)