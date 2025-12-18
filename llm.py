import json
import os
import re
import random
from openai import OpenAI

try:
    from rag import get_relevant_context
except ImportError:
    def get_relevant_context(text): return ""

with open(os.path.join(os.path.dirname(__file__), "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

conversation_history = []
exam_state = {
    "stage": "idle", 
    "turn_count": 0,
    "part2_topic": "" 
}

START_TRIGGERS = {"start", "begin", "ok start", "okay start", "let's start"}

PART1_TOPICS = [
    "Hometown", "Home/Accommodation", "Hobbies", 'weather'
    "Describe a person you admire",
    "Describe a traditional festival",
    "Describe a journey you went on",
    "Describe a piece of technology you use",
    "Describe a skill you learned recently"
]

PART2_TOPICS = [
    "Describe a person you admire",
    "Describe a traditional festival",
    "Describe a journey you went on",
    "Describe a piece of technology you use",
    "Describe a skill you learned recently"
]

def reset_exam():
    global conversation_history, exam_state
    conversation_history = []
    exam_state = {
        "stage": "part1", 
        "turn_count": 0, 
        "part2_topic": ""
    }

def get_next_system_instruction(user_input: str) -> str:
    stage = exam_state["stage"]
    count = exam_state["turn_count"]

    grammar_rule = (
        "GRAMMAR CHECKING RULES:\n"
        "1. Check the user's latest input for OBJECTIVE errors (tense, preposition, article).\n"
        "2. IF (and ONLY IF) there is an error, start output with: 'Quick fix: [Correction]'.\n"
        "3. IF input is a COMMAND (e.g., 'change topic', 'stop', 'I don't know'), DO NOT fix grammar. Just accept it.\n"
        "4. Do NOT nitpick. If it sounds natural, ignore it.\n"
    )

    if stage == "part1":
  
        target_topic = random.choice(PART1_TOPICS)
        return (
            f"{grammar_rule}\n"
            f"CURRENT STAGE: Part 1 (Round {count + 1}/3).\n"
            f"TASK: 1. (Optional) Quick fix grammar. 2. Ask ONE simple question about '{target_topic}'.\n"
            "Keep the question short."
        )

    if stage == "part2_intro":
        topic = exam_state["part2_topic"]
        return (
            "CURRENT STAGE: Part 2 (Introduction).\n"
            "TASK: Ignore previous user input context. \n"
            f"OUTPUT EXACTLY THIS: 'Part 2: [Q1/5] {topic}. You should say what it is, when you did it, and explain why...'\n"
            "Do NOT ask any other question yet."
        )

    if stage == "part2_followup":
        q_num = count + 2 
        return (
            f"{grammar_rule}\n"
            f"CURRENT STAGE: Part 2 (Follow-up Question {q_num}/5).\n"
            "TASK: 1. (Optional) Quick fix grammar. 2. Ask ONE deeper discussion question related to the topic.\n"
            f"Format starts with: '[Q{q_num}/5] ...'"
        )

    if stage == "scoring":
        return (
            "CURRENT STAGE: Finished.\n"
            "TASK: Give a Band Score (0-9) and brief feedback based on the whole conversation."
        )

    return "System Idle."

def simple_sanitize(text: str) -> str:
    if not text: return ""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        l = line.strip()
        if not l: continue
        if l.lower().startswith("current stage"): continue
        if l.lower().startswith("task"): continue
        cleaned.append(l)
    return "\n".join(cleaned)

def generate_response(user_message: str) -> str:
    global conversation_history, exam_state

    clean_input = (user_message or "").lower().strip()

    if clean_input in START_TRIGGERS or (len(conversation_history) == 0 and exam_state["stage"] == "idle"):
        reset_exam()
        opener = f"Good afternoon. Let's start Part 1. {random.choice(PART1_TOPICS)}. Do you like it?"
        conversation_history.append({"role": "user", "content": "Start"})
        conversation_history.append({"role": "assistant", "content": opener})
        return opener

    if exam_state["stage"] == "scoring":
        return "The exam is finished. Say 'start' to try again."
    current_stage = exam_state["stage"]
    current_count = exam_state["turn_count"]
    if current_stage == "part1":
        exam_state["turn_count"] += 1
        if exam_state["turn_count"] >= 3:
            exam_state["stage"] = "part2_intro"
            exam_state["turn_count"] = 0
            exam_state["part2_topic"] = random.choice(PART2_TOPICS)
            
    elif current_stage == "part2_intro":
        exam_state["stage"] = "part2_followup"
        exam_state["turn_count"] = 0
        
    elif current_stage == "part2_followup":
        exam_state["turn_count"] += 1

        if exam_state["turn_count"] >= 4:
            exam_state["stage"] = "scoring"

    system_instruction = get_next_system_instruction(user_message)
    
    conversation_history.append({"role": "user", "content": user_message})

    messages = [
        {"role": "system", "content": system_instruction},

        *conversation_history[-50:] 
    ]

    context = get_relevant_context(user_message)
    if context:
        messages.insert(1, {"role": "system", "content": f"VOCABULARY HELPER (Optional use): {context}"})

    try:

        response = client.chat.completions.create(
            model=config["model"],
            messages=messages,
            temperature=0.2 
        )
        
        raw_reply = response.choices[0].message.content.strip()
        final_reply = simple_sanitize(raw_reply)
        
        conversation_history.append({"role": "assistant", "content": final_reply})
        
        return final_reply

    except Exception as e:
        print(f"LLM Error: {e}")
        return "Sorry, please say that again."