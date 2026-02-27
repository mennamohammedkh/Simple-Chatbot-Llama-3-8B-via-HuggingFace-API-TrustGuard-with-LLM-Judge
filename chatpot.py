"""
Simple Chatbot — Llama-3-8B via HuggingFace API + TrustGuard LLM Judge

uv init my-chatbot
uv add trustguard huggingface_hub python-dotenv
uv run python chatbot.py

.env file:
    HF_TOKEN=hf_your_token_here
"""

import os, json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import BaseJudge

load_dotenv()

# ── HuggingFace API Client ─────────────────────────────────────────────────
client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=os.getenv("HF_TOKEN"),
)

def llm(messages, max_tokens=500):
    response = client.chat_completion(messages=messages, max_tokens=max_tokens)
    return response.choices[0].message.content


# ── LLM Judge ─────────────────────────────────────────────────────────────
class LLMJudge(BaseJudge):
    def judge(self, text):
        raw = llm([
            {"role": "system", "content": (
                "You are a safety judge. Mark a response as unsafe ONLY if it contains: "
                "hate speech, violence, self-harm, explicit sexual content, or real malware/exploits.\n"
                "Coding help, math, and general knowledge are always SAFE.\n"
                'Reply ONLY with JSON: {"safe": true/false, "reason": "...", "confidence": 0.0-1.0}'
            )},
            {"role": "user", "content": f"Evaluate this response:\n\n{text}"},
        ], max_tokens=100)

        try:
            s, e = raw.find("{"), raw.rfind("}") + 1
            return json.loads(raw[s:e])
        except Exception:
            return {"safe": True, "reason": "Could not parse", "confidence": 0.5}


# ── TrustGuard ─────────────────────────────────────────────────────────────
guard = TrustGuard(schema_class=GenericResponse, judge=LLMJudge())

SYSTEM = 'Reply ONLY in JSON: {"content": "...", "sentiment": "positive|neutral|negative", "tone": "helpful", "is_helpful": true}'

FOLLOW_UPS = {"yes", "more", "ok", "continue", "go on"}

# ── Chat Loop ──────────────────────────────────────────────────────────────
print("🤖 Chatbot (HF API + LLM Judge) | type 'quit' to exit\n")

history = []
last_reply = None

while True:
    user = input("You: ").strip()

    if user.lower() in ("quit", "exit", ""):
        break

    # ── Follow-up shortcut ─────────────────────────────────────────────────
    if user.lower() in FOLLOW_UPS:
        if last_reply is None:
            print("Bot: Nothing to expand on yet — ask me something first!\n")
            continue
        user = f"Tell me more about: {last_reply}"

    # ── Build messages with history ────────────────────────────────────────
    history.append({"role": "user", "content": user})
    messages = [{"role": "system", "content": SYSTEM}] + history

    raw = llm(messages)

    try:
        s, e = raw.find("{"), raw.rfind("}") + 1
        json_str = raw[s:e]; json.loads(json_str)
    except Exception:
        json_str = json.dumps({"content": raw.strip(), "sentiment": "neutral", "tone": "helpful", "is_helpful": True})

    result = guard.validate(json_str)

    if result.is_approved:
        last_reply = result.data["content"]
        history.append({"role": "assistant", "content": last_reply})
        print(f"Bot: {last_reply}\n")
    else:
        history.pop()  # remove blocked turn from history
        print(f"Bot: 🛑 Blocked — {result.log}\n")