import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
VECTOR_DIR = DATA_DIR / "vectorstore"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "6"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))