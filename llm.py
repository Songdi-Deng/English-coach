import json
import os
from openai import OpenAI

from rag import get_relevant_context  # ← NEW

with open(os.path.join(os.path.dirname(__file__), "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

with open(os.path.join(os.path.dirname(__file__), "prompts.json"), "r", encoding="utf-8") as f:
    prompts = json.load(f)

prompt = prompts[config["prompt_mode"]]
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

conversation_history = [{"role": "system", "content": prompt}]


def generate_response(user_message: str) -> str:
    # 1) Get context from your course books via RAG
    context = get_relevant_context(user_message)

    # 2) Keep your normal chat history
    conversation_history.append({"role": "user", "content": user_message})
    limited_history = [conversation_history[0]] + conversation_history[-10:]

    # 3) Extend messages with a system message containing the retrieved context
    messages = list(limited_history)  # shallow copy
    if context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "You are an English coach. Use the following course book "
                    "excerpts as additional context when answering. "
                    "If the answer is not in them, still answer from your own knowledge.\n\n"
                    f"{context}"
                ),
            }
        )

    # 4) Call your local Ollama model as before
    response = client.chat.completions.create(
        model=config["model"],
        messages=messages,
        temperature=config.get("temperature", 0.7),
    )

    assistant_reply = response.choices[0].message.content.strip()
    conversation_history.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply
