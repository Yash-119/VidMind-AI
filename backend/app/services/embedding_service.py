from pathlib import Path

from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_DIR = PROJECT_ROOT / "models"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

print("Loading embedding model...")
print("Model cache:", MODEL_DIR)

model = SentenceTransformer(
    MODEL_NAME,
    cache_folder=str(MODEL_DIR)
)

print("Embedding model loaded successfully.")


def create_embeddings(texts: list[str]):

    if not texts:
        return []

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return embeddings
