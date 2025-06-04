# TalentScout Hiring Assistant Chatbot
#[[Link to the website](https://talentscout-hiring-assistant.streamlit.app)]
## Project Overview
TalentScout is an intelligent hiring assistant chatbot for tech recruitment agencies. It collects essential candidate details and generates tailored technical interview questions based on a candidate's declared tech stack using OpenAI GPT, all via a simple web chat interface.

## Features
- Friendly, guided candidate onboarding (name, contact, experience, tech stack, etc)
- OpenAI-powered dynamic technical question generation per technology
- Context- and flow-managed chat UX (exit anytime)
- Fully local session and privacy-respecting (no persistent PII storage)

## Installation Instructions
1. **Clone the repo:**
   ```sh
   git clone <repo-url>
   cd talentscout-hiring-assistant
   ```
2. **Install dependencies:**
   ```sh
   pip install streamlit openai
   pip install requirments.txt
   ```
3. **Run the app:**
   ```sh
   streamlit run streamlit_app.py
   ```

## Usage Guide
1. Follow the chatbot prompts to enter candidate info step by step.
2. At the end, paste your OpenAI API key when prompted (or set via env var/secrets) to generate tailored technical questions based on the tech stack you list.
3. Exit/chat log and persona are fully visible as you interact.

## Technical Details
- **Frontend:** Python/Streamlit
- **LLM Integration:** OpenAI GPT-3.5 or GPT-4 via `openai` Python API
- **Prompt Design:** Prompts instruct GPT to create 3–5 technical questions for *each* technology in the candidate's stack, tailored to their years of experience. (See below for more on prompt design)
- **Validation:** Email and phone field validation, plus exit-word detection
- **No persistent storage:** All candidate data is ephemeral/session-local

## Prompt Engineering
- Chat prompts are crafted to maximize clarity and relevance. I specify:
    - Each tech in the stack should elicit 3-5 concise, challenging questions
    - Experience years are used by GPT for appropriate difficulty
    - Prompts include: "Format as bulleted lists, one per technology."
- Example prompt fragment:
  > Generate 3-5 interview questions for EACH technology listed in this tech stack: Python, Django, PostgreSQL. Questions should be concise, on-point, ...

## Data Handling & Privacy
- **No candidate PII is saved or transmitted to any backend.** Everything is processed in memory in the session only.

- **API keys** should be managed via Streamlit secrets or environment variables—not put in code.

## Challenges & Solutions
- **Multi-tech-stack prompt design:** Handling both breadth (many techs) and depth (good quality per tech) in a single prompt is a challenge; carefully tuned prompts and GPT output parsing help maximize relevant results.





## License
Created by Anurodh
