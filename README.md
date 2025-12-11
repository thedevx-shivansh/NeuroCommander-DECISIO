WebApp Link : https://neurocommander-decisio.onrender.com/

⚡ NeuroCommander D.E.C.I.S.I.O. — Executive Decision Engine 

“When your brain freezes… this system doesn’t.”

🌪️ Why I Built This 

We all have that moment.

You stare at two paths.
Your brain loops the same thoughts.
You feel stuck, anxious, overthinking everything.

Welcome to decision paralysis — the silent killer of ambition.

I built NeuroCommander D.E.C.I.S.I.O. because I was tired of soft, vague advice from normal AI chatbots. I wanted something that could think — something that could take a messy human dilemma and break it down like a seasoned executive with zero patience for nonsense.

Here’s the deal:
This isn’t a “chatbot.”
It’s a 3-stage cognitive machine built to give one thing:

A final, absolute decision backed by brutal reasoning.
🧠 What NeuroCommander Actually Does

NeuroCommander is a multi-stage AI reasoning pipeline that behaves like your personal decision boardroom.

Stage 1 — Deep Cognitive Analysis (Gemini 3 Pro Preview)

The system becomes Dr. NeuroCommand Synthesis — a cold, surgical analyst.

It extracts:

Core dilemma
Raw emotions
Hidden psychological patterns
Cognitive distortions
Long-term outcome simulations

This is powered by Gemini 3 Pro preview with a high reasoning mode using a massive system instruction block built into the backend.

Stage 2 — Executive Arbitration (Gemini 3 Pro Preview)

Now it switches into The NeuroCommander, a ruthless decision engine.

It:

Picks ONE option
Justifies it with strategic logic
Outlines risks & mitigations
Issues a strict action plan
Reframes your identity
No emotional fluff.
No “both sides.”
Just orders.

Stage 3 — JSON Finalizer (Gemini 2.5 Flash exp)

This stage forces everything into a perfect JSON schema:

Emotions
Distortions
Decision
Rationale
Action plan
Risks
Affirmation
Timestamps

Flash runs at temperature 0, so the output is stable, clean, and UI-ready.
The final JSON is parsed directly by your Cosmic UI frontend.

🚀 Tech Stack (The Arsenal)
🔥 Frontend: Cosmic UI

Pure HTML5, CSS3, and vanilla JS
Animated starfield background
Glowing neon UI
Smooth transitions
Interactive action plan cards
In-browser JSON download & history viewer

⚙️ Backend: NeuroCommander Core

Flask 3 server
Gunicorn for production
Google-genai v0.1.0 
Custom 3-stage pipeline (analysis → arbitration → JSON formatting)
Enterprise-level logging
Full session-based authentication
Google OAuth 2.0 support

🗄️ Database: Smart Switch Architecture

SQLite locally
Auto-switches to PostgreSQL on Render (environment-based)
Stores user accounts + past decisions

🔐 Security

Email/password authentication
Password hashing
Google OAuth login
Session cookies
CORS enabled

🌌 The Vibe (Why It Feels Different)

NeuroCommander is built to feel like you’re talking to a futuristic decision console — something between Iron Man’s JARVIS and a Navy captain who refuses excuses.

The UI is cosmic.
The output is sharp.
The tone is cold but helpful.

This isn’t meant to make you feel good.
It’s meant to make you move.

🧪 How to Use -

You don’t install anything.

👉 Just go to the website- https://neurocommander-decisio.onrender.com/
👉 Log in (Email or Google).
👉 Type your dilemma (20–3000 chars).
👉 Hit “Analyze.”
👉 Wait 15–40 seconds.

The 3-stage pipeline kicks in:

Stage 1: Deep Psychological Analysis
Stage 2: Hard Decision (Commander tone)
Stage 3: JSON Finalizer → polished decision UI

You get:

The final decision
Reasoning
Risks
Action plan
Identity frame
Downloadable JSON

That’s it.
One screen → full executive clarity.



🛠️ For Developers (Running Locally)


If you still want to run it locally:

1️⃣ Clone the repo
git clone https://github.com/thedevx-shivansh/NeuroCommander-DECISIO.git
cd neurocommander

2️⃣ Install dependencies

From requirements.txt 

pip install -r requirements.txt

3️⃣ Add your .env
GEMINI_API_KEY=your_key_here
SECRET_KEY=your_flask_secret
GOOGLE_CLIENT_ID=your_oauth_client_id
DATABASE_URL=optional_for_render

4️⃣ Run the server
python main.py

5️⃣ Open the UI
http://localhost:3000


Done.

🧬 Under the Hood 

Here’s the deal:

Most AI apps try to be friendly.
NeuroCommander tries to be right.

The power comes from:

Brutally specific system prompts
Mmulti-model chaining (Pro → Pro → Flash)
Deep psychological reasoning logic
Deterministic JSON formatting
Front-end rendering that feels like a sci-fi cockpit.
Every dilemma turns into a structured, high-resolution decision framework.

That’s why judges love it.
It feels alive, but disciplined.

🏁 Why This Matters

Because people don’t need more tools that “help you think.”

They need tools that:

Call out your distortions
Predict long-term outcomes
Remove noise
Give ONE decision
Tell you what to do TODAY

NeuroCommander acts like a personal executive advisor, powered by Gemini 3 Pro preview and backed by a rock-solid backend .

This isn’t a productivity tool.
It’s a clarity machine.


🧾 License

Proprietary & Confidential — All Rights Reserved.

This project is built for:
Hackathons
Kaggle Competitions
Portfolio
Research
Internal demos
Do not redistribute or modify without permission.

Author: Shivansh Arora
Role: Lead & Solo Developer & Designer
Event: Gemini Vibe Code Hackathon 2025
