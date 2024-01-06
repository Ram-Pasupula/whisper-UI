from flask import Flask, render_template, request
from flask_cors import CORS  # Import CORS from flask_cors
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for your Flask app

# Replace this URL with the actual URL of your FastAPI service
BACKEND_API_URL = "http://127.0.0.1:8000/transcode"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]

        if file:
            try:
                response = transcode_file(file)
                return render_template("result.html", result=response)
            except Exception as e:
                return render_template("error.html", error=str(e))

    return render_template("index.html")


def transcode_file(file):
    files = {"file": (file.filename, file.stream, file.mimetype)}
    data = {
        "task": "transcribe",
        "lang": "en",
        "output": "txt",
    }

    response = requests.post(BACKEND_API_URL, files=files, data=data)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    app.run(debug=True)
