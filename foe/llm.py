"""LLM gateway via litellm proxy on :4000."""
import os
import requests

GATE_URL = os.environ.get("LITELLM_GATE", "http://127.0.0.1:4000")


def call(model: str, system: str, user: str, temperature: float = 0.7) -> str:
    """Send a chat completion request to the litellm gate. Returns the assistant text."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
    }
    try:
        resp = requests.post(f"{GATE_URL}/v1/chat/completions", json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[LLM error: {e}]"
