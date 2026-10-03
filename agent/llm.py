import os
import json
import requests

from .config import LLM_PROVIDER, OPENAI_MODEL, OLLAMA_MODEL


def extract_json(text):
    """
    Try to extract JSON from LLM output.
    Handles plain JSON, code fences, and partial JSON.
    """
    if text is None:
        return {}

    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1

        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

    return {"answer": text}


def llm_json(messages):
    """
    Call LLM and return parsed JSON object.
    Supports OpenAI and Ollama.
    """

    if LLM_PROVIDER == "openai":
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is missing. Set it in .env or use Ollama."
            )

        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL")
)

        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0,
                response_format={"type": "json_object"}
            )
        except Exception:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0
            )

        content = response.choices[0].message.content
        return extract_json(content)

    elif LLM_PROVIDER == "ollama":
        payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0
            }
        }

        response = requests.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        content = response.json().get("message", {}).get("content", "")
        return extract_json(content)

    else:
        raise ValueError("Unsupported LLM_PROVIDER. Use openai or ollama.")