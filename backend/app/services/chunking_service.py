from pathlib import Path
import json


# ==========================================
# CHUNK CONFIGURATION
# ==========================================

MAX_CHUNK_WORDS = 120

MIN_CHUNK_WORDS = 20


# ==========================================
# CREATE TRANSCRIPT CHUNKS
# ==========================================

def create_chunks(transcript_path: str):

    transcript_file = Path(transcript_path)

    if not transcript_file.exists():
        raise FileNotFoundError(
            f"Transcript file not found: {transcript_file}"
        )

    # --------------------------------------
    # Load transcript
    # --------------------------------------

    with transcript_file.open(
        "r",
        encoding="utf-8"
    ) as file:

        transcript_data = json.load(file)

    segments = transcript_data.get(
        "segments",
        []
    )

    if not segments:
        raise ValueError(
            "No transcript segments found."
        )

    chunks = []

    current_text = []
    current_start = None
    current_end = None
    current_word_count = 0

    # ======================================
    # PROCESS WHISPER SEGMENTS
    # ======================================

    for segment in segments:

        text = segment.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        start = segment.get(
            "start",
            0
        )

        end = segment.get(
            "end",
            start
        )

        words = text.split()

        # ----------------------------------
        # Start new chunk
        # ----------------------------------

        if current_start is None:

            current_start = start

        # ----------------------------------
        # Add segment
        # ----------------------------------

        current_text.append(text)

        current_end = end

        current_word_count += len(words)

        # ----------------------------------
        # Chunk limit reached
        # ----------------------------------

        if current_word_count >= MAX_CHUNK_WORDS:

            chunks.append({

                "chunk_id":
                    len(chunks) + 1,

                "start":
                    current_start,

                "end":
                    current_end,

                "text":
                    " ".join(current_text),

                "word_count":
                    current_word_count
            })

            # Reset

            current_text = []

            current_start = None

            current_end = None

            current_word_count = 0

    # ======================================
    # ADD REMAINING TEXT
    # ======================================

    if current_text:

        chunks.append({

            "chunk_id":
                len(chunks) + 1,

            "start":
                current_start,

            "end":
                current_end,

            "text":
                " ".join(current_text),

            "word_count":
                current_word_count
        })

    # ======================================
    # MERGE VERY SMALL FINAL CHUNK
    # ======================================

    if len(chunks) > 1:

        last_chunk = chunks[-1]

        if (
            last_chunk["word_count"]
            < MIN_CHUNK_WORDS
        ):

            previous_chunk = chunks[-2]

            previous_chunk["text"] += (
                " " +
                last_chunk["text"]
            )

            previous_chunk["end"] = (
                last_chunk["end"]
            )

            previous_chunk["word_count"] += (
                last_chunk["word_count"]
            )

            chunks.pop()

    return {

        "language":
            transcript_data.get(
                "language"
            ),

        "duration":
            transcript_data.get(
                "duration"
            ),

        "total_chunks":
            len(chunks),

        "chunks":
            chunks
    }


# ==========================================
# SAVE CHUNKS
# ==========================================

def save_chunks(
    transcript_path: str,
    output_path: str
):

    chunk_data = create_chunks(
        transcript_path
    )

    output_file = Path(
        output_path
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_file.open(
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
        f"Created {chunk_data['total_chunks']} chunks."
    )

    print(
        f"Chunks saved to: {output_file}"
    )

    return str(output_file)