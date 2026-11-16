from pathlib import Path
import chromadb


# ==========================================
# CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"
VECTOR_DB_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# CHROMA CLIENT
# ==========================================

client = chromadb.PersistentClient(
    path=str(VECTOR_DB_DIR)
)


# ==========================================
# GET VIDEO COLLECTION
# ==========================================

def get_collection(video_id: str):

    collection_name = f"video_{video_id}"

    collection = client.get_or_create_collection(
        name=collection_name,

        # IMPORTANT:
        # Use cosine distance for semantic search.
        metadata={
            "description":
                "VidMind AI video knowledge base",

            "hnsw:space":
                "cosine"
        }
    )

    return collection


# ==========================================
# STORE CHUNKS
# ==========================================

def store_chunks(
    video_id: str,
    chunks: list,
    embeddings
):

    collection = get_collection(
        video_id
    )

    ids = []
    documents = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        chunk_id = str(
            chunk.get(
                "chunk_id",
                index + 1
            )
        )

        ids.append(
            f"{video_id}_{chunk_id}"
        )

        documents.append(
            chunk["text"]
        )

        metadatas.append({

            "video_id":
                video_id,

            "chunk_id":
                chunk_id,

            "start":
                float(chunk["start"]),

            "end":
                float(chunk["end"]),

            "word_count":
                int(chunk["word_count"])
        })

    collection.add(

        ids=ids,

        documents=documents,

        embeddings=embeddings.tolist(),

        metadatas=metadatas
    )

    print(
        f"Stored {len(chunks)} chunks "
        f"for video {video_id}"
    )

    return collection.count()
