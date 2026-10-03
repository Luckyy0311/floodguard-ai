# FloodGuard AI

**Real-Time Flood Risk Assessment and Emergency Response Agent using Retrieval-Augmented Generation (RAG) and Agentic AI**

FloodGuard AI is an intelligent decision-support system that combines live meteorological data, official alert feeds, a retrieval-augmented knowledge base, and an autonomous agent architecture to provide location-specific flood risk assessments and actionable emergency guidance.

---

## Table of Contents

1. [Overview](#overview)
2. [Problem Statement](#problem-statement)
3. [Proposed Solution](#proposed-solution)
4. [Key Features](#key-features)
5. [System Architecture](#system-architecture)
6. [Agentic Workflow](#agentic-workflow)
7. [Technology Stack](#technology-stack)
8. [Repository Structure](#repository-structure)
9. [Installation](#installation)
10. [Configuration](#configuration)
11. [Usage](#usage)
12. [Data Sources and APIs](#data-sources-and-apis)
13. [Knowledge Base](#knowledge-base)
14. [Docker Deployment](#docker-deployment)
15. [Limitations](#limitations)
16. [Future Enhancements](#future-enhancements)
17. [Safety Disclaimer](#safety-disclaimer)
18. [License](#license)
19. [Author](#author)

---

## Overview

During flood events, affected populations require fast, location-specific, and actionable information. Conventional systems typically provide static guidance or generic chatbot responses that are neither real-time nor grounded in verified preparedness material.

FloodGuard AI addresses this gap by deploying an autonomous agent that reasons over live environmental data and a curated emergency-preparedness knowledge base. The system evaluates flood risk quantitatively, retrieves relevant safety procedures through semantic search, and produces structured, prioritized emergency recommendations.

---

## Problem Statement

Existing flood-information systems suffer from the following limitations:

- Static content that does not reflect current weather conditions.
- Generic responses that are not specific to the user's location.
- Absence of quantified risk assessment.
- No integration between live data sources and preparedness documentation.
- Limited actionability of the guidance provided.

---

## Proposed Solution

FloodGuard AI implements an agentic pipeline that:

1. Resolves the user's location into geographic coordinates.
2. Retrieves live precipitation and probability data for the next 24 hours.
3. Queries official alert services where available.
4. Computes a quantitative flood risk score (0 to 100).
5. Retrieves relevant preparedness guidance using vector-based semantic search.
6. Synthesizes a structured response containing risk level, recommended actions, and source attribution.

---

## Key Features

- **Agentic tool orchestration:** The language model autonomously selects and sequences tool calls rather than responding from static training data.
- **Real-time data integration:** Live weather and geocoding data via the Open-Meteo API; official alerts via the National Weather Service API.
- **Quantitative risk engine:** A rule-based scoring model derived from current precipitation, 24-hour rainfall accumulation, precipitation probability, and severe weather codes.
- **Retrieval-Augmented Generation:** Semantic search over local flood-safety, evacuation, and emergency-contact documents using Sentence Transformers embeddings.
- **Explainable reasoning:** A full tool-call trace is exposed in the interface for transparency and auditability.
- **Provider flexibility:** Supports OpenAI-compatible endpoints (OpenAI, Groq, OpenRouter) and fully local inference via Ollama.
- **Containerized deployment:** Docker support for reproducible environments.

---

## System Architecture

```text
                        +-----------------------+
                        |     User Query (UI)   |
                        +-----------+-----------+
                                    |
                                    v
                        +-----------------------+
                        |    FloodGuard Agent   |
                        |   (LLM Reasoning Core)|
                        +-----------+-----------+
                                    |
        +-------------+-------------+-------------+--------------+
        |             |             |             |              |
        v             v             v             v              v
+---------------+ +-----------+ +------------+ +-----------+ +------------+
| Geocoding API | | Weather   | | Official   | | RAG       | | Emergency  |
| (Open-Meteo)  | | Risk API  | | Alerts API | | Retrieval | | Contacts   |
+---------------+ +-----------+ +------------+ +-----------+ +------------+
        |             |             |             |              |
        +-------------+-------------+-------------+--------------+
                                    |
                                    v
                        +-----------------------+
                        | Risk Level + Actions  |
                        | + Sources + Trace     |
                        +-----------------------+
```

---

## Agentic Workflow

For a query such as *"Assess the flood risk for Chennai"*, the agent executes the following sequence:

1. `geocode_location` — resolves "Chennai" to latitude and longitude.
2. `get_weather_risk` — retrieves live precipitation metrics and computes the risk score.
3. `get_official_alerts` — checks for active flood-related warnings at the coordinates.
4. `search_preparedness_docs` — retrieves relevant safety guidance from the knowledge base.
5. Final synthesis — returns a structured report with risk level, recommended actions, and sources.

Each intermediate tool call and its result are recorded and displayed in the interface under **Agent Tool Trace**.

---

## Technology Stack

| Component        | Technology                                    |
|------------------|-----------------------------------------------|
| Application UI   | Streamlit                                     |
| Agent Framework  | Custom Python agent loop with JSON tool calls |
| Language Models  | OpenAI / Groq / OpenRouter / Ollama           |
| Embeddings       | Sentence Transformers (all-MiniLM-L6-v2)      |
| Vector Search    | NumPy cosine similarity store                 |
| Weather Data     | Open-Meteo Forecast and Geocoding APIs        |
| Alert Data       | National Weather Service (NWS) Alerts API     |
| Deployment       | Docker                                        |

---

## Repository Structure

```text
floodguard-ai/
├── app.py                     # Streamlit application entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
├── .env.example               # Environment variable template (safe to commit)
├── .gitignore                 # Excludes .env and build artifacts
├── README.md
├── agent/
│   ├── __init__.py
│   ├── config.py              # Paths and environment configuration
│   ├── llm.py                 # LLM client (OpenAI-compatible and Ollama)
│   ├── prompts.py             # System prompt and tool specifications
│   ├── rag.py                 # Vector store and semantic retrieval
│   ├── tools.py               # Geocoding, weather, alerts, contacts tools
│   └── core.py                # Agent orchestration loop
└── data/
    ├── docs/                  # RAG source documents
    │   ├── flood_safety.txt
    │   ├── evacuation_checklist.txt
    │   └── emergency_contacts.txt
    └── vectorstore/           # Generated embeddings (gitignored)
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Git
- An API key from OpenAI, Groq, or OpenRouter (or a local Ollama installation)

### Step 1: Clone the Repository

```bash
git clone https://github.com/<your-username>/floodguard-ai.git
cd floodguard-ai
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Note: The first run downloads the Sentence Transformers embedding model (approximately 90 MB).

### Step 4: Configure Environment Variables

Create your local environment file from the template:

```bash
# macOS / Linux
cp .env.example .env

# Windows
copy .env.example .env
```

Open `.env` and insert your credentials. See the [Configuration](#configuration) section for provider-specific values.

### Step 5: Launch the Application

```bash
streamlit run app.py
```

The interface will be available at:

```text
http://localhost:8501
```

---

## Configuration

All configuration is performed through the `.env` file. The `.env` file is excluded from version control and must never be committed.

### Environment Variables

| Variable          | Description                                  | Default       |
|-------------------|----------------------------------------------|---------------|
| `LLM_PROVIDER`    | `openai` or `ollama`                         | `openai`      |
| `OPENAI_API_KEY`  | API key for OpenAI-compatible provider       | —             |
| `OPENAI_MODEL`    | Model identifier                             | `gpt-4o-mini` |
| `OPENAI_BASE_URL` | Custom endpoint for Groq / OpenRouter        | —             |
| `OLLAMA_MODEL`    | Local model name when using Ollama           | `llama3.1`    |
| `MAX_TOOL_CALLS`  | Maximum agent reasoning steps per query      | `6`           |
| `REQUEST_TIMEOUT` | HTTP timeout in seconds for external APIs    | `20`          |

### Provider Examples

**OpenAI**

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=<your-openai-key>
OPENAI_MODEL=gpt-4o-mini
```

**Groq (free tier)**

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=<your-groq-key>
OPENAI_MODEL=openai/gpt-oss-120b
OPENAI_BASE_URL=https://api.groq.com/openai/v1
```

**OpenRouter (free models)**

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=<your-openrouter-key>
OPENAI_MODEL=meta-llama/llama-3.3-70b-instruct:free
OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

**Ollama (fully local, no API key required)**

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1
```

When using Groq or OpenRouter, ensure the client in `agent/llm.py` is initialized with the base URL:

```python
client = OpenAI(
    api_key=api_key,
    base_url=os.getenv("OPENAI_BASE_URL")
)
```

---

## Usage

### Chat Interface

Enter natural-language queries in the chat input at the bottom of the page. The agent will autonomously determine which tools to invoke.

### Live Risk Check

Use the **Run Live Risk Check** button in the sidebar to generate an immediate risk assessment for the configured default location without typing a query.

### Default Location

The **Default Location** field in the sidebar is used whenever a query does not explicitly specify a place name.

### Rebuilding the Knowledge Base

After modifying documents in `data/docs/`, click **Rebuild Knowledge Base** in the sidebar to regenerate embeddings.

### Example Queries

| Query | Demonstrates |
|---|---|
| Assess the current flood risk for Chennai. | Geocoding, live weather, risk scoring |
| Check live weather and flood alerts for Houston, Texas. | Official alert integration |
| What should I do if flood water enters my house? | RAG retrieval |
| Provide a complete emergency evacuation checklist. | RAG retrieval and synthesis |
| Check the flood risk for Miami and list the items I should pack for evacuation. | Multi-tool agentic chaining |

### Interpreting the Output

Each response includes:

- **Answer:** A structured markdown report.
- **Risk Level:** One of `low`, `elevated`, `moderate`, `high`, or `unknown`.
- **Recommended Actions:** Prioritized safety steps.
- **Sources:** Attribution to APIs and knowledge-base documents.
- **Agent Tool Trace:** An expandable log of every tool call and result, demonstrating the agent's reasoning path.

---

## Data Sources and APIs

| Source | Purpose | Authentication |
|---|---|---|
| Open-Meteo Geocoding API | Place-name to coordinate resolution | None required |
| Open-Meteo Forecast API | Live precipitation and probability data | None required |
| NWS Alerts API | Official active weather alerts (United States) | None required |
| Local document store | Flood safety, evacuation, and contact guidance | Not applicable |

---

## Knowledge Base

The RAG component indexes the plain-text documents located in `data/docs/`:

- `flood_safety.txt` — Pre-flood, during-flood, and post-flood safety procedures.
- `evacuation_checklist.txt` — Evacuation preparation and shelter guidance.
- `emergency_contacts.txt` — Emergency communication protocols and contact templates.

Documents are chunked with overlap, embedded using `all-MiniLM-L6-v2`, and retrieved via cosine similarity. Additional `.txt` files placed in `data/docs/` are automatically included upon knowledge-base rebuild.

---

## Docker Deployment

Build the image:

```bash
docker build -t floodguard-ai .
```

Run the container (pass your key at runtime so it is never stored in the image):

```bash
docker run -p 8501:8501 --env-file .env floodguard-ai
```

Access the application at `http://localhost:8501`.

---

## Limitations

- Official alert coverage via the NWS API is limited to United States coordinates; other regions rely on the meteorological risk engine alone.
- The risk score is a heuristic indicator and is not a substitute for hydrological or hydraulic flood modelling.
- System behaviour depends on the availability of external APIs.
- Emergency contact information is templated and must be localized for production deployment.

---

## Future Enhancements

- Integration of satellite-derived flood extent data and river gauge levels.
- Geographic visualization of risk zones on an interactive map.
- Persistent storage of assessments and alert history in a relational database.
- Multilingual response generation.
- Outbound notification channels (SMS, email, WhatsApp) for proactive alerts.
- Migration of the retrieval layer to a production vector database.

---

## Safety Disclaimer

FloodGuard AI is an academic decision-support prototype. It is not an official emergency service and must not be relied upon as the sole source of safety information during an actual flood event. Always follow instructions issued by local authorities and official disaster-management agencies.

---

## License

This project is released under the MIT License for academic and educational use.

---

## Author

**Abdul Mofique Siddiqui**  
Contact: mofique7860@gmail.com 
