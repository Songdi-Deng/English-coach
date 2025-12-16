from flask import Flask, render_template, request, jsonify
from tts import speak_text
from stt import transcribe_speech
from llm import generate_response
import os

try:
    from rag import get_collection
except ImportError:
    print("Warning: rag.py not found or dependencies missing.")
    def get_collection(): pass

app = Flask(__name__, static_folder="static")

with app.app_context():
    print("🚀 Pre-loading RAG database...")
    get_collection()

@app.route("/")
def index():
    return render_template("final_index.html")

@app.route("/process_audio", methods=["POST"])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    file_path = "temp.wav"
    audio_file.save(file_path)

    transcript, lang = transcribe_speech(file_path)
    print(f"User (STT): [{transcript}]")

    if not transcript or len(transcript.strip()) < 2:
        fallback_msg = "I didn't catch that. Could you say it again?"
        audio_path = os.path.join("static", "audio_reply.mp3")
        speak_text(fallback_msg, audio_path)

        return jsonify({
            "user": "(Silence or unclear)",
            "assistant": fallback_msg,
            "audio_url": f"/{audio_path}"
        })

    reply = generate_response(transcript)
    print("Assistant:", reply)

    audio_path = os.path.join("static", "audio_reply.mp3")
    speak_text(reply, audio_path)
    
    return jsonify({
        "user": transcript,
        "assistant": reply,
        "audio_url": f"/{audio_path}"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)