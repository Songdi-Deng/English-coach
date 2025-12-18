import google.generativeai as genai
import os
import time

# ======================================
# ⚠️ Google Gemini API Key
# ======================================
GOOGLE_API_KEY = ""
genai.configure(api_key=GOOGLE_API_KEY)

def transcribe_speech(file_path="temp.wav"):
    if not os.path.exists(file_path):
        print(f" STT Error: File not found at {file_path}")
        return "", "error"

    try:
        print(f" Uploading audio: {file_path}...")
        audio_file = genai.upload_file(file_path)

        while audio_file.state.name == "PROCESSING":
            print("Processing audio on Google servers...")
            time.sleep(0.5)
            audio_file = genai.get_file(audio_file.name)

        if audio_file.state.name == "FAILED":
            print(" STT Error: Audio processing failed on Google side.")
            return "", "error"

        print(" Audio Ready. Generating transcript...")

        model = genai.GenerativeModel("gemini-2.5-pro")

        prompt = """
        You are an expert English transcriber. 
        Your task is to transcribe the audio content **STRICTLY IN ENGLISH**.

        ### RULES:
        1. **Language**: Output ONLY English. 
           - If the audio is Chinese/Foreign, translate the core meaning to English if possible, or ignore it.
           - If it is Silence or just Noise, output NOTHING (empty string).
        2. **Formatting**: Fix capitalization and punctuation. (e.g., "i like it" -> "I like it.")
        3. **No Filler**: Remove stuttering (um, ah, uh).
        """
    
        response = model.generate_content([prompt, audio_file])
        if not response.parts:
            print(" STT Warning: Gemini returned no text (Silence/Blocked).")
            return "", "empty"

        transcribed_text = response.text.strip()
        if not transcribed_text:
            return "", "empty"

        return transcribed_text, "en"

    except Exception as e:
        print(f" API Critical Error: {e}")
        return "", "error"