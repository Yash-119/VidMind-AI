from app.services.search_service import search_video


# ==========================================
# VIDEO ID
# ==========================================

VIDEO_ID = "5327e520-5e95-4de1-a1c2-99de9ce924f1"


# ==========================================
# QUESTION
# ==========================================

QUESTION = "What is web Development?"


# ==========================================
# SEARCH
# ==========================================

print()
print("==============================")
print("VIDMIND SEMANTIC SEARCH")
print("==============================")
print()

print(
    f"Question: {QUESTION}"
)

print()

results = search_video(
    VIDEO_ID,
    QUESTION,
    top_k=5
)


# ==========================================
# DISPLAY RESULTS
# ==========================================

if not results:

    print(
        "No relevant results found."
    )

else:

    for result in results:

        print("--------------------------------")
        print(
            f"Rank: {result['rank']}"
        )

        print(
            f"Chunk: {result['chunk_id']}"
        )

        print(
            f"Timestamp: "
            f"{result['start']:.2f}s"
            f" → "
            f"{result['end']:.2f}s"
        )

        print(
            f"Similarity: "
            f"{result['similarity']}"
        )

        print()

        print(
            result["text"]
        )

        print()


# ==========================================
# SUCCESS
# ==========================================

print("==============================")
print("SEMANTIC SEARCH TEST COMPLETE")
print("==============================")