import json
import os
from openai import OpenAI

try:
    from rag import get_relevant_context
except ImportError:
    print("Warning: rag.py not found. Running without context retrieval.")
    def get_relevant_context(text): return ""

with open(os.path.join(os.path.dirname(__file__), "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

conversation_history = []

def generate_response(user_message: str) -> str:
    """
    Loading
    """
 
    context = get_relevant_context(user_message)

    conversation_history.append({"role": "user", "content": user_message})

    messages_to_send = list(conversation_history[-10:])

    if context:
        system_injection = {
            "role": "system",
            "content": (
                "### BACKGROUND CONTEXT (Reference Only):\n"
                f"{context}\n\n"
                "### INSTRUCTION:\n"
                "1. The user is answering an IELTS speaking question.\n"
                "2. The content above is just for your reference (e.g., to check facts or suggest vocabulary).\n"
                "3. **DO NOT** read the book to the user.\n"
                "4. **DO NOT** output exercises, steps, or lesson plans from the text.\n"
                "5. **STAY IN CHARACTER** as an IELTS Examiner. Ignore the context if it disrupts the conversation flow."
            )
        }
        messages_to_send.insert(-1, system_injection)

    try:
    
        response = client.chat.completions.create(
            model=config["model"], 
            messages=messages_to_send,
            temperature=config.get("temperature", 0.2)
        )

        assistant_reply = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply

    except Exception as e:
        print(f"LLM error: {e}")
        return "Sorry, I encountered an error processing your request."