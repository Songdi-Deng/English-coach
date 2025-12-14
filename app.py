from flask import Flask, render_template, request, jsonify
from tts import speak_text
from stt import transcribe_speech
from llm import generate_response
import os

app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    return render_template("index_jolein.html")

@app.route("/process_audio", methods=["POST"])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    file_path = "temp.wav"
    audio_file.save(file_path)

    # Transcribe the audio
    transcript, _ = transcribe_speech(file_path)
    print("User:", transcript)

    # Generate a response using Qwen3:8b
    reply = generate_response(transcript)
    print("Assistant:", reply)

    # Convert response to speech
    audio_path = os.path.join("static", "audio_reply.mp3")
    speak_text(reply, audio_path)

return jsonify({
    "user": transcript,
    "assistant": reply,
    "audio_url": f"/{audio_path}"})


