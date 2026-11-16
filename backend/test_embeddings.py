from app.services.embedding_service import create_embeddings


# ==========================================
# TEST TEXT
# ==========================================

texts = [
    "DNS converts domain names into IP addresses.",
    "A computer network allows devices to communicate."
]


print()
print("==============================")
print("Creating embeddings...")
print("==============================")
print()


embeddings = create_embeddings(texts)


print()
print("==============================")
print("EMBEDDING TEST SUCCESSFUL")
print("==============================")

print(
    f"Number of embeddings: {len(embeddings)}"
)

print(
    f"Embedding dimensions: {embeddings.shape[1]}"
)

print()
print(
    "First embedding:"
)

print(
    embeddings[0]
)