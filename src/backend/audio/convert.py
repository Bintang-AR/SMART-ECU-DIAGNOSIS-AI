import subprocess
import tempfile
import os

def webm_to_wav(webm_bytes: bytes) -> bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as webm_file:
        webm_file.write(webm_bytes)
        webm_path = webm_file.name

    wav_path = webm_path.replace(".webm", ".wav")

    subprocess.run(
        ["ffmpeg", "-y", "-i", webm_path, wav_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    with open(wav_path, "rb") as f:
        wav_bytes = f.read()

    os.remove(webm_path)
    os.remove(wav_path)

    return wav_bytes
