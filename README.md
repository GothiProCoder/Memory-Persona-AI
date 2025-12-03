<a name="readme-top"></a>

<div align="center">

# Memory Persona AI: Memory Extraction & Personality Engine

### 🧠 *An AI that doesn't just chat—it remembers, understands, and adapts.*

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge&logo=github)](https://github.com/GothiProCoder/Memory-Persona-AI/actions)
[![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge&logo=python)](https://github.com/GothiProCoder/Memory-Persona-AI/releases)
[![License](https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-orange?style=for-the-badge)](requirements.txt)
[![Code Coverage](https://img.shields.io/badge/coverage-95%25-green?style=for-the-badge)](tests/)

[Read Docs](#) • [Report Bug](../../issues) • [Request Feature](../../issues)

</div>

---

## ✨ About The Project

<img src="/assets/frontend.png" align="right" alt="Dashboard Screenshot" width="400" style="margin-left: 20px;">

> **Problem**: Most AI chatbots are ephemeral—they forget who you are the moment you close the tab. They lack context, emotional continuity, and personal connection.
>
> **Solution**: **Memory Persona AI** is an intelligent conversation engine that bridges this gap. By actively extracting memories, tracking emotional patterns, and adapting its personality, it creates a deeply personalized and persistent user experience.

Memory Persona AI isn't just another wrapper around an LLM. It's a sophisticated system that listens, learns, and evolves with every interaction. It's designed for developers who want to build more human-like AI experiences.

### Key Highlights
- **🧠 Active Memory Extraction**: Automatically analyzes conversations to extract user preferences, hobbies, and life events.
- **🎭 Dynamic Personality Engine**: Transforms responses to match specific personas (e.g., Professional, Witty, Empathetic).
- **❤️ Emotional Intelligence**: Detects and tracks emotional triggers and patterns over time.

### Built With
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1.0+-1C3C3C?style=flat-square&logo=chainlink&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini%202.5%20Flash-4285F4?style=flat-square&logo=google&logoColor=white)

<details open>
<summary>📸 <b>See More Screenshots</b></summary>
<br>
<div align="center">
  <img src="/assets/frontend.png" alt="Frontend">
  <p><i>Frontend</i></p>
  <br>
  <img src="/assets/memory-core.png" alt="Memory Core">
  <p><i>Memory Core</i></p>
  <br>
  <img src="/assets/extracted-emotional-patterns.png" alt="Memory Core">
  <p><i>Extracted Emotional Patterns</i></p>
  <br>
  <img src="/assets/Manual-Memory-Extraction.png" alt="Memory Core">
  <p><i>Manual Memory Extraction</i></p>
</div>
</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🚀 Features

<details open>
<summary>Click to view detailed Feature Breakdown</summary>

### Core Capabilities

*   **Memory & Context**
    *   ✅ **Structured Extraction**: Extracts facts, preferences, and emotional states into structured JSON profiles.
    *   ✅ **Short-term Persistence**: Stores user profiles for continuous context across the same FastAPI session.
    *   ⬜ **Vector Search**: Semantic search over past conversations (Planned).

*   **Personality & Interaction**
    *   ✅ **Adaptive Persona**: Switch between distinct personalities like "The Mentor" or "The Comedian" on the fly.
    *   ✅ **Tone Analysis**: Adjusts response style based on the user's current emotional state.
    *   ✅ **Real-time Transformation**: Intercepts and rewrites standard LLM outputs to match the active persona.

*   **Developer Experience**
    *   ✅ **RESTful API**: Fully documented FastAPI endpoints.
    *   ✅ **Interactive UI**: Polished Streamlit dashboard for testing and visualization.
    *   ✅ **Modular Agents**: Decoupled architecture for easy extension of agents.

</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🏗️ Architecture

Memory Persona AI follows a modular microservices-ready architecture, separating the cognitive agents from the API layer and the frontend interface.

### System Design
1.  **Frontend (Streamlit)**: Captures user input and renders the chat interface and memory dashboard.
2.  **API Gateway (FastAPI)**: Routes requests, handles authentication (dev), and manages session state.
3.  **Cognitive Agents (LangChain)**:
    *   **Memory Agent**: runs in the background to analyze chat history.
    *   **Personality Agent**: intercepts responses to apply stylistic transformations.
4.  **Model Layer (Google Gemini)**: The underlying LLM providing reasoning and generation capabilities.
5.  **Storage**: In-memory or persistent storage for user profiles and chat logs.

### Folder Structure
```bash
Memory-Persona-AI/
├── agents/             # Cognitive logic (Memory, Personality)
│   ├── memory_extraction_agent.py
│   └── personality_engine_agent.py
├── config/             # App configuration & env vars
├── frontend/           # Streamlit UI application
│   ├── components/     # UI widgets (Chat, Sidebar)
│   └── styles/         # Custom CSS
├── models/             # LLM configurations (Gemini)
├── routes/             # API endpoints (FastAPI)
├── schemas/            # Pydantic models for data validation
├── store/              # Data persistence layer
└── main.py             # Application entry point
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## ⚡ Quick Start

### Prerequisites
*   Python 3.10 or higher
*   A Google Cloud Project with Gemini API access

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/GothiProCoder/Memory-Persona-AI.git
    cd Memory-Persona-AI
    ```

2.  **Set up the backend environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

<a name="step-3"></a>

3.  **Run this in the terminal (MANDATORY)**
    ```bash
    pip uninstall -y langchain-google-genai langchain_google_genai langchain-core langchain
    pip cache purge

    # install latest releases (explicit)
    pip install "langchain-core" "langchain-google-genai" "langchain"
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the root directory.

    | Variable | Description | Default |
    |:---|:---|:---|
    | `GOOGLE_API_KEY` | **Required**. Your Google Cloud API Key for Gemini. | N/A |
    | `MODEL_NAME` | The Gemini model version to use. | `gemini-2.5-flash` |

5.  **Run the Backend Server**
    ```bash
    uvicorn main:app --port 8000
    # Uvicorn running at http://localhost:8000
    ```

6.  **Run the Frontend Dashboard** (in a new terminal)
    ```bash
    cd frontend
    pip install -r requirements.txt
    streamlit run app.py
    # Dashboard running at http://localhost:8501
    ```

### Common Issues
<details open>
<summary>Click to view Troubleshooting Guide</summary>
<br>
| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'langchain_core.pydantic_v1'` | Follow (<a href="#step-3">Step 3</a>) |
| `ModuleNotFoundError` | Ensure you activated the virtual environment and installed requirements. |
| `Google API Error` | Verify your `GOOGLE_API_KEY` is valid and has Gemini API access enabled. |

</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 📖 Usage Examples

### API Endpoints

| Method | Endpoint | Description |
|:---:|---|---|
| `GET` | `/api/v1/health` | Check system status |
| `POST` | `/api/v1/memory/extract` | Trigger memory extraction analysis |
| `GET` | `/api/v1/memory/user/{id}` | Retrieve a user's psychological profile |
| `POST` | `/api/v1/personality/transform` | Rewrite text with a specific persona |

### Extract Memory (Python Example)

```python
import requests

url = "http://localhost:8000/api/v1/memory/extract"
payload = {
    "user_id": "user_123",
    "messages": [
        {"role": "user", "content": "I love hiking in the Alps on weekends."}
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

**Response:**
```json
{
  "user_preferences": ["Likes outdoor activities", "Prefers mountains"],
  "emotional_patterns": [{"state": "Joy", "frequency": "frequent"}],
  "memorable_facts": [{"fact": "Hikes in Alps", "importance": "high"}]
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 📝 License & Contact

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Maintainer**: GothiProCoder   
**LinkedIn**: [@ Gotham Chand U](https://www.linkedin.com/in/gotham-chand/)

<div align="center">
  <sub>Built with ❤️ by GothiProCoder.</sub>
</div>
