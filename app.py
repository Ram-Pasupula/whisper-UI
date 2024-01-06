from flask import Flask, render_template, request
from flask_cors import CORS
import requests
import os
import tempfile
import wave
import pyaudio

app = Flask(__name__)
CORS(app)

BACKEND_API_URL = "http://127.0.0.1:8000/transcode"

# Define constants for audio recording
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5  # Adjust the recording duration as needed

# Create a temporary directory to store recorded audio files
TEMP_DIR = tempfile.mkdtemp()

# PyAudio setup
audio = pyaudio.PyAudio()


@app.route("/", methods=["GET", "POST"])
def index():
    response_text = None
    if request.method == "POST":
        if "file" in request.files:
            # If a file is provided, proceed with file upload
            file = request.files["file"]
            try:
                response_text = transcode_file(file)
            except Exception as e:
                return render_template("error.html", error=str(e))
        else:
            # If no file is provided, start audio recording
            audio_file_path = record_audio()
            try:
                response_text = transcode_file(audio_file_path)
            except Exception as e:
                return render_template("error.html", error=str(e))

    return render_template("index.html", response_text=response_text)


def transcode_file(file):
    if isinstance(file, str):
        files = {"file": open(file, "rb")}
    else:
        files = {"file": (file.filename, file.stream, file.mimetype)}
    params = {
        "task": "transcribe",
        "lang": request.form["lang"],
        "output": request.form["output"],
    }

    response = requests.post(BACKEND_API_URL, files=files, params=params)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


def record_audio():
    audio_file_path = os.path.join(TEMP_DIR, "recorded_audio.wav")
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("Recording audio...")

    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()

    # Save the recorded audio to a WAV file
    wf = wave.open(audio_file_path, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    return audio_file_path


if __name__ == "__main__":
    app.run(debug=True)
