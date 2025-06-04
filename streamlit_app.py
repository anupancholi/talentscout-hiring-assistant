from datetime import datetime
import streamlit as st
import re
import os

import base64

try:
    import openai
    OPENAI_LIB_OK = True
except ImportError:
    OPENAI_LIB_OK = False


def load_openai_api_key():
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    elif "OPENAI_API_KEY" in os.environ:
        return os.environ["OPENAI_API_KEY"]
    else:
        return ""

# ---- Custom CSS for UI  ----


def inject_custom_css():
    st.markdown('''
        <style>
            .stApp { background: #f7fafd; }
            .ts-header {
                display: flex; align-items: center; padding: 1.3rem 2rem;
                background: linear-gradient(90deg, #3b82f6 40%, #5a67d8); border-radius: 16px 16px 0 0;
                margin-bottom: 0.8rem;
            }
            .ts-header-icon {
                margin-right: 1.3rem; font-size: 2.8rem; color: #fff; background: #fff2; padding: 0.7rem; border-radius: 12px;
            }
            .ts-header-titles {
                color: #fff; flex: 1;
            }
            .ts-title-lg { font-size: 1.5rem; font-weight: bold; letter-spacing: 0.03em; }
            .ts-title-sm { font-size: 1.01rem; opacity: 0.8; font-weight: 400; }
            .ts-chatbox {
                background: #2563eb11; border-radius: 18px; margin: 0 0.6rem; padding: 1.1rem 2rem 2.8rem 2rem;
                box-shadow: 0 4px 18px #0001;
            }
            .ts-hr {
                border: none; border-top: 1.5px solid #e0e5ef; margin: 0.7em 0 1.0em 0;
            }
            .ts-chat-title {
                background: linear-gradient(90deg, #3b82f6 60%, #5a67d8 120%);
                color: #fff; padding: 0.6rem 1rem; border-radius: 10px 10px 0 0;
                font-size: 1.22rem; font-weight: bold; margin-bottom: 1rem; display: flex; align-items: center;
            }
            .ts-chat-title-icon { margin-right: 0.6rem; font-size: 1.2rem; }
            .ts-bubble {
                background: #f4f7fa; margin: 0.6rem 0; padding: 1rem 1.5rem 0.6rem 1.5rem;
                border-radius: 12px; max-width: 650px; box-shadow: 0 1px 8px #0001; font-size: 1.13rem; position: relative;
            }
            .ts-bubble-user {
                background: #fff; border: 1px solid #e2e8f0; margin-left: auto; color: #393e46;
            }
            .ts-bubble-bot {
                background: #f4f7fa; color: #222a3f;
            }
            .ts-msg-time {
                font-size: 0.85rem; color: #789; opacity: 0.55; margin-top: 0.38rem;
            }
            .ts-footer {
                background: #fff; border-top: 1.5px solid #e4e8f3; bottom: 0; left: 0; width: 100%;
                padding: 1.2rem 1.4rem; position: fixed; display: flex; align-items: center;
            }
            .ts-txt-input {
                width: 100%; border: 1.3px solid #c4d1f9; border-radius: 10px; font-size: 1.14rem;
                padding: 0.7rem 1.2rem; background: #f8fafd; margin-right: 1rem;
            }
            .ts-send-btn {
                background: #3b82f6; color: #fff; border: none; border-radius: 9px;
                padding: 0.7rem 1.2rem; font-size: 1.24rem; cursor: pointer;
            }
            .ts-send-btn:hover { background: #2769d0; }
            .ts-download-wrap { text-align: right; margin: 0.55em 0 0.65em 0; }
        </style>
    ''', unsafe_allow_html=True)


inject_custom_css()

questions = [
    ("Full Name", "May I have your full name please?"),
    ("Email Address", "What is your email address?"),
    ("Phone Number", "What is your phone number?"),
    ("Years of Experience", "How many years of experience do you have in tech roles?"),
    ("Desired Position(s)", "What position(s) are you applying for?"),
    ("Current Location", "Where are you currently located? (City, Country)"),
    ("Tech Stack", "List your programming languages, frameworks, databases, and tools you are proficient in.")
]

# ---- Initialize session state ----
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'greeted' not in st.session_state:
    st.session_state.greeted = False
if 'candidate_info' not in st.session_state:
    st.session_state.candidate_info = {f: '' for f, _ in questions}
if 'transcript' not in st.session_state:
    st.session_state.transcript = []
if 'ended' not in st.session_state:
    st.session_state.ended = False
if 'tech_questions' not in st.session_state:
    st.session_state.tech_questions = []

# Header and chatbox UI
st.markdown('<div class="ts-header">'
            '<span class="ts-header-icon">🗂️</span>'
            '<div class="ts-header-titles"><div class="ts-title-lg">TalentScout AI Assistant</div>'
            '<div class="ts-title-sm">Initial Candidate Screening</div></div>'
            '</div>', unsafe_allow_html=True)
st.markdown('<div class="ts-chatbox">', unsafe_allow_html=True)
st.markdown('<div class="ts-chat-title"><span class="ts-chat-title-icon">🤖</span>Hiring Assistant</div>',
            unsafe_allow_html=True)


def render_bubble(msg, who="bot", show_time=True, is_first=False):
    ts = datetime.now().strftime("%I:%M:%S %p")
    style = "ts-bubble "
    style += "ts-bubble-user" if who == "user" else "ts-bubble-bot"
    timestamp = f'<div class="ts-msg-time">{ts}</div>' if show_time else ''
    bubble = f'<div class="{style}">{msg}{timestamp}</div>'
    st.markdown(bubble, unsafe_allow_html=True)


# Show greeting
if st.session_state.step == 0 and not st.session_state.greeted:
    welcome = "Hello! 👋 Welcome to TalentScout's AI Hiring Assistant. I'm here to help with your initial screening process. Let's get started!<br><br>May I have your full name please?"
    render_bubble(welcome, who="bot", show_time=True, is_first=True)
    st.session_state.greeted = True

# Re-render previous transcript
for msg, who in st.session_state.transcript:
    render_bubble(msg, who=who, show_time=True)

# Validators


def is_valid_email(email): return re.match(
    r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]{2,}", email)


def is_valid_phone(phone): return re.match(r"^[+\d][\d\-\s]{6,}$", phone)


# Chat input flow
current_step = st.session_state.step
ended = st.session_state.ended
field, question = (questions[current_step]
                   if current_step < len(questions) else (None, None))

if not ended and field:
    def submit():
        user_input = st.session_state['user_input'].strip()
        if not user_input:
            st.stop()
        if user_input.lower() in ["exit", "quit", "stop", "bye", "end"]:
            st.session_state.transcript.append((user_input, "user"))
            st.session_state.transcript.append(
                ("Thank you for your time. The conversation has ended. We appreciate your interest!", "bot"))
            st.session_state.ended = True
            st.session_state.step = len(questions)
            st.session_state['user_input'] = ''
            st.rerun()
        valid = True
        if field == "Email Address" and not is_valid_email(user_input):
            render_bubble("Please enter a valid email address.", who="bot")
            valid = False
        elif field == "Phone Number" and not is_valid_phone(user_input):
            render_bubble("Please enter a valid phone number.", who="bot")
            valid = False
        elif len(user_input.strip()) < 2:
            render_bubble("Please provide a valid response.", who="bot")
            valid = False
        if valid:
            st.session_state.candidate_info[field] = user_input
            st.session_state.transcript.append((user_input, "user"))
            if current_step + 1 < len(questions):
                st.session_state.transcript.append(
                    (questions[current_step+1][1], "bot"))
            st.session_state.step += 1
            st.session_state['user_input'] = ''
            st.rerun()

    st.markdown("""
        <form class="ts-footer" onsubmit="return false;">
            <input name="response" id="MainInput" class="ts-txt-input" placeholder="Type your response..." maxlength="80">
            <button class="ts-send-btn" type="submit" onclick="window.parent.streamlitSend({type:'streamlit:sendMessage',data:document.getElementById('MainInput').value});return false;">✈️</button>
        </form>
        <script>
            window.addEventListener('load', function() {
                var inp = window.parent.document.querySelector('input#MainInput');
                if(inp) inp.focus();
            });
        </script>
    """, unsafe_allow_html=True)
    st.text_input("Your response:", key="user_input", placeholder="Type your response...",
                  max_chars=80, label_visibility="collapsed", on_change=submit)

elif not ended and not field:
    finish_msg = "Thank you for providing your information! Next, I'll ask you a few technical questions based on your tech stack."
    st.session_state.transcript.append((finish_msg, "bot"))
    st.session_state.ended = True
    st.rerun()

# Download transcript


def transcript_to_text():
    return "\n".join([f"[{'AI' if who == 'bot' else 'You'}]: {msg}" for msg, who in st.session_state.transcript])


if st.session_state.transcript and st.session_state.ended:
    transcript_txt = transcript_to_text()
    st.markdown('<div class="ts-download-wrap">', unsafe_allow_html=True)
    st.download_button("Download Transcript (.txt)",
                       transcript_txt, file_name="talentscout_conversation.txt")
    st.markdown('</div>', unsafe_allow_html=True)

# Technical question generation


def generate_tech_questions(tech_stack, years_exp, model="gpt-3.5-turbo", api_key=None):
    prompt = (
        f"You are a technical interviewer for a technology recruitment agency. "
        f"Generate 3-5 interview questions for EACH technology listed in this tech stack: {tech_stack}. "
        f"Questions should be concise, on-point, and appropriate for someone with {years_exp} years of experience. "
        f"Format the output as Bulleted lists, one per technology."
    )
    if not (OPENAI_LIB_OK and api_key):
        return ["[Unable to generate questions: OpenAI package or API key missing]"]
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful technical interviewer."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = completion.choices[0].message.content
        return raw.strip().split("\n")
    except Exception as e:
        return [f"[Error generating questions: {e}]"]


if st.session_state.ended and all(v.strip() for v in st.session_state.candidate_info.values()):
    api_key = load_openai_api_key()
    if not api_key:
        api_key = st.text_input(
            "Enter your OpenAI API Key to generate questions:", type="password")
    if api_key and OPENAI_LIB_OK:
        if not st.session_state.tech_questions:
            with st.spinner("Generating technical questions with OpenAI GPT..."):
                st.session_state.tech_questions = generate_tech_questions(
                    st.session_state.candidate_info['Tech Stack'],
                    st.session_state.candidate_info['Years of Experience'],
                    api_key=api_key
                )
        st.markdown('<hr class="ts-hr">', unsafe_allow_html=True)
        render_bubble(
            "Here are the technical interview questions customized for your tech stack:", who="bot", show_time=False)
        for q in st.session_state.tech_questions:
            if q.strip():
                render_bubble(q, who="bot", show_time=False)
    elif not OPENAI_LIB_OK:
        render_bubble(
            "OpenAI Python package is not installed. Please run 'pip install openai'.", who="bot")
    else:
        render_bubble(
            "Add your OpenAI API key above and press Enter to generate questions.", who="bot")

st.markdown('</div>', unsafe_allow_html=True)
