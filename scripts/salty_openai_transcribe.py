#!/usr/bin/env python3
"""OpenAI word-timestamp transcription into ai-video-editor's normalized JSON."""
import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
import requests

def transcribe(source, out):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    source = Path(source).resolve()
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "voice.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(source), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)], check=True)
        with wav.open("rb") as f:
            r = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": "Bearer " + key},
                files={"file": ("voice.wav", f, "audio/wav")},
                data=[("model", "whisper-1"), ("response_format", "verbose_json"), ("timestamp_granularities[]", "word"), ("language", "en")],
                timeout=240,
            )
        r.raise_for_status()
        data = r.json()
    words = [{"text": w["word"], "start": float(w["start"]), "end": float(w["end"]), "speaker": "speaker_0"} for w in data.get("words", [])]
    if not words:
        raise RuntimeError("Transcription returned no word timestamps")
    duration = float(data.get("duration") or words[-1]["end"])
    normalized = {"source": str(source), "engine": "openai-whisper-1", "words": words, "events": [], "duration": duration}
    out.write_text(json.dumps(normalized, indent=2), encoding="utf-8")
    print(str(out))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("source")
    p.add_argument("output")
    a = p.parse_args()
    transcribe(a.source, a.output)
