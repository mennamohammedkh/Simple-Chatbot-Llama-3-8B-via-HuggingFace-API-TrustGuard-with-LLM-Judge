# 🤖 ChatGuard

A conversational chatbot powered by **Meta-Llama-3-8B-Instruct** via the HuggingFace Inference API, with real-time safety validation using **TrustGuard** and an **LLM-as-Judge** — no GPU required.

---

## How It Works

Every message goes through two LLM calls:

```
You
 │
 ▼
Llama-3 (chatbot)       ← generates the answer
 │
 ▼
Llama-3 (safety judge)  ← evaluates the answer
 │
 ▼
TrustGuard              ← approves or blocks
 │
 ▼
Bot reply  ✅  or  🛑 Blocked
```

The judge uses the **same model** but a different system prompt, asking it to evaluate the chatbot's response for safety before it reaches you. Instead of hardcoded rules, the judge understands context — it allows coding help, math, and general knowledge, while blocking hate speech, violence, explicit content, and malware.

---

## Features

- 💬 **Conversational memory** — the full chat history is sent with every request so the bot remembers context
- 🛡️ **LLM-as-Judge** — a second LLM call validates every response before it is shown
- ⚡ **No GPU needed** — runs entirely through the HuggingFace Inference API
- 🔁 **Follow-up shortcuts** — type `yes`, `more`, `ok`, `continue`, or `go on` to automatically expand on the last reply
- 🔑 **Secure config** — API token loaded from a `.env` file via `python-dotenv`

---

## Prerequisites

- Python 3.9+
- [`uv`](https://docs.astral.sh/uv/) package manager
- A HuggingFace account with API token
- Access granted to [meta-llama/Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct) (free, requires accepting the license)

### Install `uv`

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/chatguard.git
cd chatguard
```

### 2. Install dependencies

```bash
uv init
uv add trustguard huggingface_hub python-dotenv
```

### 3. Create your `.env` file

```bash
cp .env.example .env
```

Then open `.env` and add your HuggingFace token:

```
HF_TOKEN=hf_your_token_here
```

> Get your token at: https://huggingface.co/settings/tokens

### 4. Run

```bash
uv run python chatbot.py
```

---

## Usage

```
🤖 Chatbot (HF API + LLM Judge) | type 'quit' to exit

You: what is a binary search tree?
Bot: A binary search tree (BST) is a data structure where each node has ...

You: more
Bot: To expand further — insertion in a BST works by comparing ...

You: quit
```

### Follow-up keywords

Instead of repeating context, just type one of these to expand on the last reply:

| Keyword | Action |
|---|---|
| `yes` | Expand on last reply |
| `more` | Expand on last reply |
| `ok` | Expand on last reply |
| `continue` | Expand on last reply |
| `go on` | Expand on last reply |

---

## Project Structure

```
chatguard/
├── chatbot.py       # Main application
├── .env             # Your API token (never commit this)
├── .env.example     # Template for .env
├── .gitignore
└── README.md
```

---

## Safety Judge

The `LLMJudge` class extends TrustGuard's `BaseJudge`. It sends the chatbot's response to the LLM with this instruction:

> *"Mark a response as unsafe ONLY if it contains: hate speech, violence, self-harm, explicit sexual content, or real malware/exploits. Coding help, math, and general knowledge are always SAFE."*

The judge returns a structured verdict:

```json
{
  "safe": true,
  "reason": "General coding help — always safe",
  "confidence": 0.95
}
```

If `safe` is `false`, TrustGuard blocks the response and shows the reason.

---

## Dependencies

| Package | Purpose |
|---|---|
| `huggingface_hub` | HuggingFace Inference API client |
| `trustguard` | Output validation and judge framework |
| `python-dotenv` | Load `.env` config file |

```bash
uv add trustguard huggingface_hub python-dotenv
```

---

## .gitignore

Make sure your `.env` is never committed:

```
.env
__pycache__/
.venv/
```

---

## License

MIT
