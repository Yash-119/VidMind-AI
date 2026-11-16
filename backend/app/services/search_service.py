from app.services.embedding_service import create_embeddings
from app.services.vector_service import get_collection


# ==========================================
# SEARCH CONFIGURATION
# ==========================================

MAX_DISTANCE = 1.0


# ==========================================
# SEMANTIC VIDEO SEARCH
# ==========================================

def search_video(
    video_id: str,
    question: str,
    top_k: int = 5
):

    if not question or not question.strip():
        return []

    question = question.strip()

    collection = get_collection(
        video_id
    )

    count = collection.count()

    print()
    print("===================================")
    print("VIDEO SEARCH")
    print("===================================")
    print("Video ID:", video_id)
    print("Chunks:", count)
    print("Question:", question)
    print()

    if count == 0:

        print(
            "No chunks found."
        )

        return []

    # --------------------------------------
    # Question embedding
    # --------------------------------------

    question_embedding = create_embeddings(
        [question]
    )

    # --------------------------------------
    # Chroma search
    # --------------------------------------

    results = collection.query(

        query_embeddings=
            question_embedding.tolist(),

        n_results=min(
            top_k,
            count
        ),

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    search_results = []

    # --------------------------------------
    # Process results
    # --------------------------------------

    for index in range(
        len(documents)
    ):

        distance = distances[index]

        metadata = metadatas[index]

        similarity = 1 - distance
        relevance = max(0.0, min(1.0, similarity)) * 100
        accuracy = relevance

        print(
            f"Result {index + 1}: "
            f"distance={distance:.4f}, "
            f"similarity={similarity:.4f}, "
            f"relevance={relevance:.2f}%, "
            f"accuracy={accuracy:.2f}%"
        )

        if distance > MAX_DISTANCE:
            continue

        search_results.append({

            "rank":
                len(search_results) + 1,

            "chunk_id":
                metadata.get(
                    "chunk_id"
                ),

            "start":
                metadata.get(
                    "start",
                    0
                ),

            "end":
                metadata.get(
                    "end",
                    0
                ),

            "text":
                documents[index],

            "distance":
                round(
                    distance,
                    4
                ),

            "similarity":
                round(
                    similarity,
                    4
                ),

            "relevance":
                round(
                    relevance,
                    2
                ),

            "accuracy":
                round(
                    accuracy,
                    2
                )
        })

    print()
    print(
        "Video context returned:",
        len(search_results)
    )

    print(
        "==================================="
    )
    print()

    return search_results
