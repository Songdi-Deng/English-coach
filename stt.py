import google.generativeai as genai
import os

# ======================================
# ⚠️ Google Gemini API Key
# ======================================
GOOGLE_API_KEY = ""
genai.configure(api_key=GOOGLE_API_KEY)

def transcribe_speech(file_path="temp.wav"):
    try:
        audio_file = genai.upload_file(file_path)
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = """
        You are an expert transcriber for an English Speaking Exam.
        Your task is to transcribe the audio content **STRICTLY IN ENGLISH**.

        ### RULES:
        1. **Language**: Output ONLY English. If the audio contains Chinese, ignore it or translate the core meaning to English.
        2. **Formatting**: You MUST fix capitalization and basic punctuation.
           - Correct: "I use AI everyday."
           - Incorrect: "i use ai everyday"
        3. **No Filler**: Remove stuttering (um, ah) to keep the text clean.
        4. **Output**: Output ONLY the raw text. No Markdown, no timestamps, no "Here is the transcript".
        """

        response = model.generate_content([prompt, audio_file])
   
        if not response.parts:
            print("❌ STT Error: Gemini returned no text (Blocked or Empty).")
            return "", "error"

        transcribed_text = response.text.strip()
        
        if not transcribed_text:
            return "", "empty"

        return transcribed_text, "en"

    except Exception as e:
        print(f"❌ API error: {e}")
        return "", "error"