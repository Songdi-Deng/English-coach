# English Speaking Coach

**English Speaking Coach** is a high-fidelity Speaking simulator. It combines the privacy and control of a locally running **Ollama** model (customized via Modelfile) with the advanced multimodal audio capabilities of **Google Gemini**.

It features a custom-defined "Examiner" model running locally for logic and reasoning, while leveraging Google Gemini for high-accuracy Speech-to-Text (STT) and natural Text-to-Speech (TTS).

---

## System Architecture

* ** The Brain (Local):** **Ollama (Custom Model)**
  * **Configuration**: Uses a custom `Modelfile` (located in `info/modelfile`) to define the strict persona and behavior of a coach.
  * **Inference**: Runs locally via Ollama (e.g., based on Qwen 2.5), ensuring low latency and privacy for the logic layer.
  * **Logic Control**: A Python-based State Machine enforces the strict exam flow (Part 1 → Part 2 → Scoring).

* **The Senses (Cloud):** **Google Gemini**
  * **Listening (`stt.py`)**: Uses Gemini (2.5 pro) for instant, accurate English transcription.
  * **Speaking (`tts.py`)**: Uses Gemini's generative audio capabilities for high-quality, natural-sounding responses.

---

## Project Structure

```text
English-coach/
│
├── app.py          # Flask server & main application logic
├── stt.py          # Google Gemini STT input (Speech-to-Text)
├── tts.py          # Google Gemini TTS output (Text-to-Speech)
├── llm.py          # Local Ollama interface + RAG integration
├── rag.py          # Retrieval-Augmented Generation pipeline
│
├── info/
│   └── modelfile   # Custom Ollama configuration file (System Prompt)
│
├── config.json     # System configuration parameters
│
├── static/
│   ├── audio_reply.mp3  # Generated TTS output
│   └── books/           # PDF and TXT course books (used by RAG)
│
└── templates/
    └── index.html       # Web UI (frontend)
Core Features
1. Custom Ollama Examiner
Defined Persona: The system uses the info/modelfile to create a dedicated model (e.g., "english-coach"). This file contains the specific System Prompts that force the model to act as a professional examiner.

2. Full-Link Gemini Audio
STT: Handles user accents and ignores non-English noise using Google's latest models.

TTS: Uses Gemini's neural generation to "act out" the examiner's lines with proper intonation.

3. RAG (Retrieval-Augmented Generation)
Supports local PDF/Textbooks in static/books/.

The system retrieves relevant vocabulary or sample answers and feeds them into the Ollama model context to provide "teacher-like" feedback.

Requirements
Software:

Ollama: Must be installed and running locally.

Python: 3.9+

Google API Key: Required for Gemini STT/TTS.

Python Libraries: (See requirements.txt)

 Setup & Usage
1. Install Dependencies
Bash

pip install -r requirements.txt
2. Setup Ollama Model
Ensure Ollama is installed.

Create the custom model using your file in info/:

Bash

ollama create english-coach -f info/modelfile
3. Configure (config.json)
Ensure config.json points to your created Ollama model name:

JSON

{
  "model": "english-coach",
  "google_api_key": "YOUR_GEMINI_API_KEY"
}
4. Run the System
Bash

python app.py
5. Start
Open your browser to http://127.0.0.1:5000.

Click the Microphone button.

Say "Start" to begin.

Workflow: You Speak → Gemini STT → Local Ollama (Custom Model) Think → Gemini TTS Speak.

Troubleshooting
Ollama Connection Error:

Ensure Ollama is running (ollama serve).

Verify the model name in config.json matches the one you created (english-coach).

Gemini Audio Errors:

Check your API Key.

If TTS fails (400 Error), check if the prompt in modelfile is strictly text-based and not asking for audio bytes directly.

Group distribution for the project:
- Songdi: Backend & Prompts & Fine tuning 
- Rachel: Frontend Design
- Jan: Backend Pipeline & Presentation
- Jolein: Frontend Design & Demonstration