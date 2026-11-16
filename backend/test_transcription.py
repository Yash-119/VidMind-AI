from pathlib import Path

from app.services.transcription_service import transcribe_audio


AUDIO_DIR = Path(r"D:\VidMind-AI\backend\audio")

TRANSCRIPT_DIR = Path(
    r"D:\VidMind-AI\backend\transcripts"
)

TRANSCRIPT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Find WAV file
audio_files = list(AUDIO_DIR.glob("*.wav"))

if not audio_files:
    print()
    print("ERROR: No WAV file found.")
    print()
    print("Upload a video first from the frontend.")
    raise SystemExit(1)


# Use the first WAV file
audio_path = audio_files[0]

transcript_path = (
    TRANSCRIPT_DIR /
    f"{audio_path.stem}.json"
)


print()
print("===================================")
print("AUDIO FILE FOUND")
print("===================================")
print(audio_path)

print()
print("===================================")
print("STARTING TRANSCRIPTION")
print("===================================")


result = transcribe_audio(
    str(audio_path),
    str(transcript_path)
)


print()
print("===================================")
print("TRANSCRIPTION COMPLETED")
print("===================================")

print()
print("Transcript saved at:")
print(result)