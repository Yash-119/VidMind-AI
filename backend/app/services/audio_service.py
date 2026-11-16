import subprocess
from pathlib import Path


def extract_audio(video_path: str, audio_path: str) -> str:

    video = Path(video_path)
    audio = Path(audio_path)

    if not video.exists():
        raise FileNotFoundError(
            f"Video file not found: {video}"
        )

    audio.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [
        "ffmpeg",
        "-y",

        # Ignore minor corrupt packets where possible
        "-err_detect", "ignore_err",

        "-i",
        str(video),

        # Select first audio stream
        "-map", "0:a:0",

        # No video
        "-vn",

        # Output format
        "-c:a", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",

        str(audio)
    ]

    print()
    print("===================================")
    print("FFMPEG AUDIO EXTRACTION")
    print("===================================")
    print("Input:", video)
    print("Output:", audio)
    print()

    try:

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

    except FileNotFoundError:

        raise RuntimeError(
            "FFmpeg is not available in PATH."
        )

    # --------------------------------------
    # Check whether useful audio was created
    # --------------------------------------

    if not audio.exists():

        raise RuntimeError(
            "FFmpeg did not create the WAV file.\n\n"
            + result.stderr[-5000:]
        )

    # --------------------------------------
    # Even if FFmpeg returned an error,
    # check whether a usable WAV exists.
    # --------------------------------------

    if audio.stat().st_size < 10000:

        raise RuntimeError(
            "FFmpeg created an invalid or empty WAV file.\n\n"
            + result.stderr[-5000:]
        )

    print()
    print("Audio extraction completed.")
    print("WAV:", audio)
    print("Size:", audio.stat().st_size, "bytes")
    print()

    return str(audio)