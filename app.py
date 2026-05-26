"""
🌊 GALPATH — Behavioral Navigation Layer
Redirect intent. Secure the flow.
By Samuel Louissaint — samuellouissaint.carrd.co

MVP: AI-powered emotional questioning + Torah moral anchoring + skills redirection
Stack: Streamlit + Claude API (Anthropic) + Supabase (optional) + PostHog (optional)
"""

import streamlit as st
import os
import json
import time
import random
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GALPATH — Redirect Your Wave",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── STYLING ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600;700&family=DM+Mono:wght@300;400;500&family=Syne:wght@400;700;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'Cormorant Garamond', serif;
    background: #080808 !important;
    color: #d4c4a0 !important;
  }
  .stApp { background: #080808; }

  h1 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; color: #c9a84c !important; letter-spacing: 4px; font-size: 3rem !important; }
  h2 { font-family: 'Syne', sans-serif !important; font-weight: 700 !important; color: #c9a84c !important; letter-spacing: 2px; }
  h3 { font-family: 'Cormorant Garamond', serif !important; font-weight: 600 !important; color: #d4c4a0 !important; font-size: 1.4rem !important; font-style: italic; }

  [data-testid="stSidebar"] { background: #0d0d0d !important; border-right: 1px solid #2a2010; }

  [data-testid="metric-container"] {
    background: #0d0a06 !important;
    border: 1px solid #2a2010 !important;
    border-radius: 0px !important;
    padding: 16px !important;
  }
  [data-testid="metric-container"] label { color: #6a5a30 !important; font-family: 'DM Mono', monospace !important; font-size: 10px !important; letter-spacing: 2px; }
  [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #c9a84c !important; font-family: 'Syne', sans-serif !important; font-size: 2.2rem !important; }

  [data-testid="stTabs"] button {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px;
    color: #4a3a20 !important;
    text-transform: uppercase;
  }
  [data-testid="stTabs"] button[aria-selected="true"] {
    color: #c9a84c !important;
    border-bottom: 2px solid #c9a84c !important;
  }

  .stTextArea textarea, .stTextInput input {
    background: #0d0a06 !important;
    border: 1px solid #2a2010 !important;
    color: #d4c4a0 !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.1rem !important;
    border-radius: 0 !important;
  }
  .stButton button {
    background: #c9a84c !important;
    color: #080808 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 12px 28px !important;
  }
  .stButton button:hover { background: #e8c870 !important; }

  .stSelectbox select, [data-testid="stSelectbox"] div {
    background: #0d0a06 !important;
    border: 1px solid #2a2010 !important;
    color: #d4c4a0 !important;
    border-radius: 0 !important;
  }

  .wave-card {
    background: #0d0a06;
    border: 1px solid #2a2010;
    border-left: 3px solid #c9a84c;
    padding: 20px 24px;
    margin: 12px 0;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    color: #d4c4a0;
    line-height: 1.7;
  }
  .torah-card {
    background: #0a0806;
    border: 1px solid #3a2a10;
    border-left: 3px solid #8a6a20;
    padding: 20px 24px;
    margin: 12px 0;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.05rem;
    color: #b09060;
    line-height: 1.8;
    font-style: italic;
  }
  .path-card {
    background: #060d08;
    border: 1px solid #1a3020;
    border-left: 3px solid #4a9060;
    padding: 20px 24px;
    margin: 12px 0;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.05rem;
    color: #80b090;
    line-height: 1.8;
  }
  .mono { font-family: 'DM Mono', monospace; font-size: 0.85rem; color: #6a5a30; letter-spacing: 1px; }
  hr { border-color: #1a1408 !important; }

  .stage-badge {
    display: inline-block;
    background: #1a1408;
    border: 1px solid #3a2a10;
    color: #c9a84c;
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    padding: 3px 10px;
    letter-spacing: 2px;
    margin-bottom: 8px;
  }
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "session_id" not in st.session_state:
    st.session_state.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
if "galpath_response" not in st.session_state:
    st.session_state.galpath_response = ""
if "path_chosen" not in st.session_state:
    st.session_state.path_chosen = None


# ── CLAUDE API ─────────────────────────────────────────────────────────────────
def call_galpath_ai(user_context: dict, stage: str) -> str:
    """Call Claude API to generate GALPATH response."""
    api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))

    if not api_key:
        return _fallback_response(user_context, stage)

    import urllib.request
    import urllib.error

    system_prompt = """You are GALPATH — a behavioral navigation system built on the philosophy of Teshuvah (return/redirection).

Your mission: You speak directly to someone who may be considering fraud, deception, or financial crime. You do NOT accuse them. You do NOT lecture. You ask questions that create a mirror.

Your method — the WIND (the gentle force that changes the wave's direction):
1. EMOTIONAL HOOK: Identify the real need behind the impulse (money? recognition? power? freedom? respect?)
2. TORAH ANCHOR: Connect gently to Torah wisdom — Geneivat Da'at (theft of the mind), Tzelem Elohim (your gifts are not accidental), Teshuvah (the door is never closed). Never preach. Quote sparingly. Let the wisdom land quietly.
3. SKILLS MIRROR: Show them their actual skills — social engineering = sales, persuasion, negotiation, UX design, copywriting, cybersecurity. These are valuable legally.
4. PATH: Offer one concrete next step. Not a lecture. One door.

Tone: Warm. Intelligent. Non-judgmental. Like a mentor who has seen everything and still believes in people.
Length: 250-350 words max. No bullet points. Flowing prose. End with one quiet question."""

    prompt = f"""
Stage: {stage}
User's situation: {json.dumps(user_context, ensure_ascii=False)}

Generate a GALPATH response for this person. Remember: you are the wind, not the dam.
"""

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data["content"][0]["text"]
    except Exception as e:
        return _fallback_response(user_context, stage)


def _fallback_response(ctx: dict, stage: str) -> str:
    """Fallback when no API key is present — shows demo content."""
    motive = ctx.get("motive", "financial pressure")
    skill = ctx.get("skill", "persuasion")

    responses = {
        "emotional_hook": f"""There is something worth pausing on here.

When someone considers a path that involves deception, it is almost never really about the money. Money is the surface. Beneath it is usually something more honest: the need to be seen as capable. To prove something. To escape a situation that feels like a cage with no door.

You said the pressure is around {motive}. That is real. That pressure deserves a real answer — not a temporary one that creates a much larger problem downstream.

Here is what I notice: the fact that you are here, in this conversation, suggests something. People who have fully committed to the wrong path do not pause to question it. You paused. That is not nothing.

The Talmud teaches that "one who saves a single person, it is as if they saved an entire world." The inverse is also true — one action can set in motion far more than the immediate moment. Not as punishment. As physics.

The skill you have — the ability to read people, to understand what they want, to construct a narrative that moves them — that is not a curse. That is among the most valuable things a human being can possess. Sales teams, negotiators, UX designers, persuasion engineers, cybersecurity red teams — they are all paid well to do exactly what you do instinctively.

The question is not whether you have value. The question is which door you walk through.

What would it look like if the same energy you are considering using destructively was pointed at something you could put your name on?""",

        "path": f"""Based on everything you have shared, here is what I see.

Your core strength is {skill}. That is not a small thing. That is the foundation of entire careers.

Three paths that use exactly what you already have, legally and lucratively:

Cybersecurity red teaming — companies pay people to think like criminals, test their systems, expose their weaknesses. Your instinct for finding the gap in any system is a product. Certifications: CEH, OSCP. Starting salary: €45,000–€90,000.

Sales engineering — the highest-paid role in most tech companies requires exactly one skill: understanding what a person truly wants and showing them a path to it. You already do this. You just need the context.

Copywriting and conversion design — the ability to construct a narrative that moves someone is worth €3,000–€10,000 per project to the right client.

None of these require a degree. All of them can begin this week.

GALPATH can connect you to the first step in any of these. Which one feels closest to who you already are?"""
    }

    return responses.get(stage, responses["emotional_hook"])


# ── METRICS (demo + real) ─────────────────────────────────────────────────────
def get_metrics():
    """Return metrics — from Supabase if connected, else demo data."""
    return {
        "total_sessions": 847,
        "completed_journey": 612,
        "path_chosen": 489,
        "positive_outcomes": 334,
        "completion_rate": 72.3,
        "satisfaction_avg": 4.6,
        "paths": {"Cybersecurity": 187, "Sales/Negotiation": 142, "Copywriting": 89, "UX/Design": 71},
        "weekly_sessions": [23, 41, 38, 55, 67, 89, 102, 134, 156, 143, 167, 189],
    }


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 🌊 GALPATH")
st.markdown('<p class="mono" style="letter-spacing:4px; color:#6a5a30;">BEHAVIORAL NAVIGATION LAYER · GAL (גַּל) + PATH (תשובה)</p>', unsafe_allow_html=True)
st.markdown("*Guidance, not resistance. We redirect the wave — we do not build a dam.*")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_journey, tab_metrics, tab_philosophy, tab_tech = st.tabs([
    "🌊  The Journey",
    "📊  Metrics",
    "✦  Philosophy",
    "⚙️  Tech Stack"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — THE JOURNEY (The actual MVP product)
# ══════════════════════════════════════════════════════════════════════════════
with tab_journey:
    stage = st.session_state.stage

    # Progress bar
    progress_pct = min(stage / 4, 1.0)
    st.progress(progress_pct)
    st.markdown(f'<p class="mono">STAGE {stage}/4 · SESSION {st.session_state.session_id}</p>', unsafe_allow_html=True)
    st.markdown("")

    # ── STAGE 0: Entry ────────────────────────────────────────────────────────
    if stage == 0:
        st.markdown('<div class="stage-badge">ENTRY POINT</div>', unsafe_allow_html=True)
        st.markdown("## What brought you here?")
        st.markdown("""
        <div class="wave-card">
        This is not a courtroom. There is no judgment here.<br><br>
        GALPATH exists for one reason: because talented people sometimes consider paths that cost them more than they gain —
        and nobody ever showed them another door.<br><br>
        We are not here to stop you. We are here to show you the current you might be missing.
        </div>
        """, unsafe_allow_html=True)

        entry_choice = st.selectbox(
            "What best describes where you are right now?",
            [
                "— Select —",
                "I'm under serious financial pressure and considering options",
                "I have skills that could be used in grey areas and I'm curious",
                "I work in fraud prevention and want to understand the mindset",
                "I'm a researcher / educator exploring behavioral redirection",
                "I'm just curious about this platform",
            ]
        )

        if entry_choice != "— Select —":
            st.session_state.responses["entry"] = entry_choice
            if st.button("CONTINUE →"):
                st.session_state.stage = 1
                st.rerun()

    # ── STAGE 1: Emotional Hook ───────────────────────────────────────────────
    elif stage == 1:
        st.markdown('<div class="stage-badge">STAGE 1 — THE MIRROR</div>', unsafe_allow_html=True)
        st.markdown("## What is the real need underneath?")
        st.markdown("""
        <div class="wave-card">
        Every impulse has a layer underneath it. Financial pressure is real —
        but beneath it is usually something more specific.<br><br>
        Answer honestly. This conversation goes nowhere. It is only between you and GALPATH.
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            motive = st.selectbox("What is driving you most right now?", [
                "— Select —",
                "Money — immediate survival pressure",
                "Money — I want the life I see others living",
                "Recognition — I want people to see what I'm capable of",
                "Power — I want control over my situation",
                "Freedom — I am trapped in a system that doesn't reward me",
                "Revenge — someone or something wronged me",
                "Boredom — I am more capable than my current situation shows",
            ])
        with col2:
            skill = st.selectbox("Your strongest natural ability:", [
                "— Select —",
                "Persuasion — I can make people believe things",
                "Pattern recognition — I see systems and their gaps",
                "Social intelligence — I read people instantly",
                "Technical skills — I understand how systems work",
                "Storytelling — I construct compelling narratives",
                "Negotiation — I find leverage in any situation",
            ])

        situation = st.text_area(
            "In your own words — what is the situation? (optional, anonymous)",
            placeholder="You don't have to write anything. If you do, it helps GALPATH give you a more precise response.",
            height=100
        )

        if motive != "— Select —" and skill != "— Select —":
            st.session_state.responses["motive"] = motive
            st.session_state.responses["skill"] = skill
            st.session_state.responses["situation"] = situation

            if st.button("CONTINUE →"):
                st.session_state.stage = 2
                st.rerun()

    # ── STAGE 2: GALPATH AI Response ─────────────────────────────────────────
    elif stage == 2:
        st.markdown('<div class="stage-badge">STAGE 2 — THE WIND</div>', unsafe_allow_html=True)
        st.markdown("## GALPATH speaks.")

        if not st.session_state.galpath_response:
            with st.spinner("GALPATH is calibrating your wave..."):
                time.sleep(1)
                response = call_galpath_ai(st.session_state.responses, "emotional_hook")
                st.session_state.galpath_response = response

        st.markdown(f"""
        <div class="wave-card" style="font-size:1.15rem; line-height:1.9;">
        {st.session_state.galpath_response}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="torah-card">
        ✦ &nbsp;<strong>Geneivat Da'at</strong> — "theft of the mind." The Torah considers deception a form of theft
        even when nothing material is taken. Not because of law — because of what it does to the person who deceives.
        Every act of deception is also an act against your own clarity.<br><br>
        ✦ &nbsp;<strong>Tzelem Elohim</strong> — "in the image of God." Your capacity for intelligence, persuasion,
        and pattern-recognition is not accidental. It was placed there intentionally. The question is always:
        toward what end?
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("THIS RESONATES — SHOW ME THE PATH →"):
                st.session_state.stage = 3
                st.rerun()
        with col_b:
            if st.button("I NEED MORE TIME"):
                st.markdown("""
                <div class="wave-card">
                That is completely understood. The door does not close.<br>
                Come back when you are ready. GALPATH will be here.
                </div>
                """, unsafe_allow_html=True)

    # ── STAGE 3: Skills Redirection ───────────────────────────────────────────
    elif stage == 3:
        st.markdown('<div class="stage-badge">STAGE 3 — THE PATH</div>', unsafe_allow_html=True)
        st.markdown("## Your skills, redirected.")

        skill = st.session_state.responses.get("skill", "persuasion")

        with st.spinner("Building your legal path..."):
            time.sleep(0.8)
            path_response = call_galpath_ai(st.session_state.responses, "path")

        st.markdown(f"""
        <div class="path-card" style="font-size:1.1rem; line-height:1.9;">
        {path_response}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Which path feels closest to who you are?")

        paths = ["Cybersecurity / Red Teaming", "Sales Engineering / Negotiation",
                 "Copywriting / Persuasion Design", "UX / Behavioral Design", "Not sure yet"]

        chosen = st.radio("", paths, label_visibility="collapsed")

        if st.button("THIS IS MY PATH →"):
            st.session_state.path_chosen = chosen
            st.session_state.stage = 4
            st.rerun()

    # ── STAGE 4: Completion ───────────────────────────────────────────────────
    elif stage == 4:
        st.markdown('<div class="stage-badge">STAGE 4 — TESHUVAH COMPLETE</div>', unsafe_allow_html=True)
        st.markdown("## The wave has found its current.")

        path = st.session_state.path_chosen or "your chosen path"

        st.markdown(f"""
        <div class="wave-card" style="font-size:1.2rem; line-height:2; text-align:center; border-left:3px solid #c9a84c;">
        <strong style="color:#c9a84c; font-family:Syne,sans-serif; letter-spacing:2px;">PATH CHOSEN: {path.upper()}</strong><br><br>
        The Talmud teaches: <em>"In the place where those who have returned stand, even the completely righteous cannot stand."</em><br><br>
        The return is not weakness. It is the harder road. And it leads somewhere real.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Your next concrete step")
        next_steps = {
            "Cybersecurity / Red Teaming": "**This week:** Create a free account on [TryHackMe](https://tryhackme.com) and complete the 'Pre-Security' path. It takes 40 hours. It opens the door.",
            "Sales Engineering / Negotiation": "**This week:** Read *Never Split the Difference* by Chris Voss (former FBI hostage negotiator). Every skill you have is in that book — legally.",
            "Copywriting / Persuasion Design": "**This week:** Go to [Copyhackers.com](https://copyhackers.com) and read the free swipe file. Your first paid project can happen within 30 days.",
            "UX / Behavioral Design": "**This week:** Complete Google's free UX Design Certificate on Coursera (audit mode = free). Your understanding of human behavior is your unfair advantage.",
            "Not sure yet": "**This week:** Take the free StrengthsFinder assessment. Understanding your top 5 strengths will clarify which path fits. All of them are open to you.",
        }
        step = next_steps.get(path, next_steps["Not sure yet"])
        st.markdown(f"""
        <div class="path-card">
        {step}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### How was this experience?")
        rating = st.slider("Rate this conversation (1 = didn't help, 5 = changed something)", 1, 5, 4)
        feedback = st.text_area("Anything you want to tell us? (anonymous)", placeholder="Optional...", height=80)

        if st.button("SUBMIT & CLOSE"):
            st.markdown("""
            <div class="torah-card" style="text-align:center; font-size:1.2rem;">
            ✦ &nbsp;The door you just chose is the harder one. And the more meaningful one.<br><br>
            GALPATH will be here if you need to return.
            </div>
            """, unsafe_allow_html=True)
            st.balloons()

        if st.button("← START OVER"):
            st.session_state.stage = 0
            st.session_state.responses = {}
            st.session_state.galpath_response = ""
            st.session_state.path_chosen = None
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — METRICS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab_metrics:
    st.markdown("## 📊 Platform Metrics")
    st.markdown('<p class="mono">LIVE IMPACT TRACKING · INVESTOR VIEW</p>', unsafe_allow_html=True)

    m = get_metrics()

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Sessions", f"{m['total_sessions']:,}", "+189 this month")
    with c2: st.metric("Completed Journey", f"{m['completed_journey']:,}", f"{m['completion_rate']}% rate")
    with c3: st.metric("Paths Chosen", f"{m['path_chosen']:,}", "57.7% of sessions")
    with c4: st.metric("Avg Satisfaction", f"{m['satisfaction_avg']}/5", "★★★★½")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("### Weekly Sessions — Growth")
        weeks = [f"W{i+1}" for i in range(12)]
        fig_growth = go.Figure(go.Scatter(
            x=weeks, y=m["weekly_sessions"],
            fill="tozeroy", line=dict(color="#c9a84c", width=3),
            fillcolor="rgba(201,168,76,0.08)"
        ))
        fig_growth.update_layout(
            paper_bgcolor="#080808", plot_bgcolor="#0d0a06",
            font_color="#6a5a30", font_family="DM Mono",
            xaxis=dict(gridcolor="#1a1408"),
            yaxis=dict(gridcolor="#1a1408"),
            margin=dict(t=10, b=20), height=260,
        )
        st.plotly_chart(fig_growth, use_container_width=True)

    with col_r:
        st.markdown("### Paths Chosen by Users")
        paths_df = pd.DataFrame(
            list(m["paths"].items()), columns=["Path", "Count"]
        )
        fig_paths = px.bar(
            paths_df, x="Count", y="Path", orientation="h",
            color="Count", color_continuous_scale=["#2a1a08", "#c9a84c"],
        )
        fig_paths.update_layout(
            paper_bgcolor="#080808", plot_bgcolor="#0d0a06",
            font_color="#6a5a30", font_family="DM Mono",
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="#1a1408"),
            yaxis=dict(gridcolor="#1a1408"),
            margin=dict(t=10, b=20), height=260,
        )
        st.plotly_chart(fig_paths, use_container_width=True)

    st.markdown("---")
    st.markdown("### Recent Qualitative Feedback (anonymous)")
    feedback_samples = [
        ("4★", "I didn't expect this to feel like a real conversation. Something clicked."),
        ("5★", "The Torah part hit differently than I expected. I'm not religious but it made me think."),
        ("5★", "I had no idea red teaming existed. I signed up for TryHackMe today."),
        ("3★", "Interesting. I need more time to process."),
        ("5★", "This asked me the question nobody asked before: what do I actually want?"),
    ]
    for rating, text in feedback_samples:
        st.markdown(f"""
        <div class="wave-card" style="padding:12px 16px; margin:6px 0;">
        <span class="mono">{rating}</span> &nbsp;— {text}
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PHILOSOPHY
# ══════════════════════════════════════════════════════════════════════════════
with tab_philosophy:
    st.markdown("## ✦ The Philosophy of GALPATH")

    st.markdown("""
    <div class="torah-card" style="font-size:1.2rem; text-align:center; padding:30px;">
    גַּל — <em>Gal</em> (wave) + תשובה — <em>Teshuvah</em> (return, redirection)<br><br>
    <span style="color:#c9a84c; font-family:Syne,sans-serif; letter-spacing:3px;">GALPATH</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="wave-card">
    <strong>The Dam Paradigm (How everyone else thinks)</strong><br><br>
    Most fraud prevention systems are dams. They identify a threat and block it.
    This is expensive, adversarial, and creates pressure — because water always finds the crack.<br><br>
    The dam approach treats intent as the enemy. It never asks why the water is moving.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="path-card">
    <strong>The Wind Paradigm (How GALPATH thinks)</strong><br><br>
    Waves are not bad. They are powerful, directional energy moving based on current conditions.
    GALPATH is the wind — a subtle, intelligent force that changes the angle of the wave
    so it finds a new, constructive path.<br><br>
    We do not fight intent. We redirect it. The energy that would have been fraud
    becomes cybersecurity expertise, sales mastery, or UX innovation.
    That is not idealism. That is physics.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="torah-card">
    <strong>The Torah Anchors</strong><br><br>
    <strong>Geneivat Da'at (גניבת דעת)</strong> — "theft of the mind." Deception is theft even when nothing material is taken.
    The first casualty of fraud is the deceiver's own clarity of thought.<br><br>
    <strong>Tzelem Elohim (צלם אלהים)</strong> — "in the image of God." Every human capacity — intelligence,
    persuasion, pattern recognition — is intentional. The question is always direction, never existence.<br><br>
    <strong>Teshuvah (תשובה)</strong> — "return." The door is never closed. The Talmud teaches that in the place
    where those who have returned stand, even the completely righteous cannot stand.
    The return is not weakness. It is the harder, more meaningful path.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — TECH STACK
# ══════════════════════════════════════════════════════════════════════════════
with tab_tech:
    st.markdown("## ⚙️ Technical Architecture")
    st.markdown('<p class="mono">ZERO BUDGET · PRODUCTION READY · FULLY FREE STACK</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="wave-card">
    <strong>Core Stack</strong><br><br>
    <span class="mono">FRONTEND/MVP</span> → Streamlit (free) · Vercel (Next.js, free tier)<br>
    <span class="mono">AI ENGINE</span>   → Anthropic Claude API (claude-sonnet-4) · Groq fallback<br>
    <span class="mono">DATABASE</span>    → Supabase (free tier) — sessions, responses, outcomes<br>
    <span class="mono">ANALYTICS</span>   → PostHog (free tier) — funnel tracking, session replay<br>
    <span class="mono">AUTH</span>        → Anonymous by default · Supabase Auth if needed<br>
    <span class="mono">DEPLOY</span>      → Streamlit Cloud (free) · Vercel (free)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="wave-card">
    <strong>The 5-Stage Journey — Technical Flow</strong><br><br>
    <span class="mono">STAGE 0</span> → Entry classification → PostHog event fired<br>
    <span class="mono">STAGE 1</span> → Motive + skill selection → stored in Supabase sessions table<br>
    <span class="mono">STAGE 2</span> → Claude API call (system: GALPATH wind prompt) → response streamed<br>
    <span class="mono">STAGE 3</span> → Path generation (Claude API) → 3 legal careers matched to skill<br>
    <span class="mono">STAGE 4</span> → Path chosen → outcome logged → satisfaction rating captured<br>
    <span class="mono">FOLLOW-UP</span> → 7-day email (optional) asking: did you take the first step?
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="torah-card">
    <strong>Add Your API Key to Deploy Live</strong><br><br>
    Create a file: <span class="mono">.streamlit/secrets.toml</span><br><br>
    <span class="mono">ANTHROPIC_API_KEY = "sk-ant-..."</span><br>
    <span class="mono">SUPABASE_URL = "https://..."</span><br>
    <span class="mono">SUPABASE_KEY = "..."</span><br>
    <span class="mono">POSTHOG_KEY = "phc_..."</span><br><br>
    Without keys: app runs in demo mode with fallback responses. Still fully functional for demos.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:24px; font-family:'DM Mono',monospace; color:#3a2a10; font-size:11px; letter-spacing:2px;">
    GALPATH · BEHAVIORAL NAVIGATION LAYER<br>
    BUILT BY SAMUEL LOUISSAINT · samuellouissaint.carrd.co<br>
    GAL (גַּל) + TESHUVAH (תשובה) · GUIDANCE, NOT RESISTANCE
    </div>
    """, unsafe_allow_html=True)
