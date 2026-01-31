# NeuroCommander D.E.C.I.S.I.O.

> **Decision Engine for Complex Human Dilemmas**  
> *Archived Hackathon Prototype*

---

## Project Status (Important)

> [!WARNING]  
> **This project is an archived hackathon prototype.**

NeuroCommander was built as part of the **Kaggle × Google DeepMind Gemini Hackathon** as an experimental system to explore **multi-stage AI reasoning and decision arbitration**.

The public web deployment is **currently inactive** due to free-tier hosting and database limitations.  
This repository is preserved for **architecture review, learning, and portfolio reference**, not as a maintained production system.

**WebApp (archived demo):**  
https://neurocommander-decisio.onrender.com/  
*(May not function due to free-tier limits)*

---

## Why I Built This

NeuroCommander was built during a hackathon to explore **how AI systems could structure decisions**, not just generate advice.

Most chatbots tend to respond with:
- multiple options  
- soft language  
- “it depends” answers  

I wanted to test the opposite idea:

> **What if an AI system was forced to pick one decision, justify it clearly, and output a structured action plan?**

NeuroCommander is **not** a general chatbot.  
It is a **decision pipeline experiment**.

---

## What NeuroCommander Does (Conceptually)

NeuroCommander is a **three-stage reasoning system** designed to take a messy human dilemma and return a **single, explicit decision**.

---

### Stage 1 — Deep Analysis  
*(Gemini 3 Pro Preview)*

- Extracts the core dilemma  
- Identifies emotional signals and cognitive distortions  
- Analyzes long-term implications  
- Produces a structured internal analysis  

This stage focuses on **understanding**, not responding.

---

### Stage 2 — Executive Arbitration  
*(Gemini 3 Pro Preview)*

- Chooses **one** option (no balancing both sides)  
- Justifies the decision using strategic reasoning  
- Lists risks and mitigation  
- Produces a strict action direction  

This stage intentionally avoids emotional comfort language.

---

### Stage 3 — JSON Finalization  
*(Gemini 2.5 Flash — deterministic)*

- Converts the decision into a fixed JSON schema:
  - `decision`
  - `rationale`
  - `risks`
  - `action_plan`
  - `timestamps`

The output is designed for **frontend rendering and programmatic use**.

---

## Why This Was Interesting to Build

This project was primarily an experiment in:

- Multi-stage model orchestration  
- Role-based system prompting  
- Deterministic vs non-deterministic outputs  
- Structured AI outputs instead of free-text replies  
- Backend → frontend integration under hackathon time pressure  

It was **not** designed to be a mental health tool or a commercial product.

---

## Tech Stack (Prototype)

### Frontend
- HTML5, CSS3, vanilla JavaScript  
- Single-page UI  
- JSON-driven rendering  

### Backend
- Python (Flask)  
- Gunicorn (deployment)  
- Google Generative AI SDK  
- Custom multi-stage reasoning pipeline  

### Database
- SQLite (local)  
- PostgreSQL (Render, environment-based auto-switch)  

### Auth & Security *(prototype-level)*
- Email/password authentication  
- Google OAuth  
- Session cookies  
- Password hashing  

---

## Notes

- This repository represents an **experimental learning phase**
- The code prioritizes **clarity over optimization**
- The system is preserved to document ideas, not to provide a live service
