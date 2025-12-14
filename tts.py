import json
import os
import re
import wave
from google import genai
from google.genai import types

# ======================================
# ⚠️ Google Gemini API Key
# ======================================
GOOGLE_API_KEY = " "

with open(os.path.join(os.path.dirname(__file__), "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

voice_name = config.get("voice")
sample_rate = int(config.get("sample_rate", 24000))
channels = int(config.get("channels", 1))
sample_width = 2 
client = genai.Client(api_key=GOOGLE_API_KEY)

def save_wave(filename, pcm_data, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)

def clean_text(text: str) -> str:
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"[#>`~]", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def speak_text(text: str, output_path: str = "static/audio_reply.wav"):
    cleaned = clean_text(text)

    if os.path.exists(output_path):
        os.remove(output_path)

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=cleaned,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            )
        )
    )

    pcm_data = response.candidates[0].content.parts[0].inline_data.data

    save_wave(output_path, pcm_data, channels=channels, rate=sample_rate, sample_width=sample_width)

    return output_path
