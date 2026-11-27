
import json
import os
import re
import html

import pandas as pd
import plotly.express as px
import streamlit as st

from pathlib import Path
from dotenv import load_dotenv

from graph.workflow import build_workflow
from agents.agent_factory import run_agent
from rag.resume_rag import extract_resume, retrieve_resume_context
from database import initialize_database, save_analysis
from auth import auth_page, logout
from dashboard import show_dashboard
from reports import markdown_report, pdf_report, skills_csv


load_dotenv()

ROOT = Path(__file__).resolve().parent

with (ROOT / "data" / "job_roles.json").open(
    "r", encoding="utf-8"
) as f:
    JOB_DATA = json.load(f)


st.set_page_config(
    page_title="CareerForge AI",
    page_icon="🚀",
    layout="wide"
)

initialize_database()


# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --ink:#172033;
    --muted:#64748b;
    --line:#e2e8f0;
    --purple:#5149b8;
    --blue:#3b82f6;
}

[data-testid="stApp"],
[data-testid="stMain"] {
    font-family:'Inter',sans-serif;
    color:var(--ink);
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 92% 3%,#e9eaff 0,transparent 28%),
        linear-gradient(145deg,#f8faff 0%,#f8fafc 52%,#f1f5fb 100%);
    color:var(--ink);
}

[data-testid="stHeader"] {
    background:transparent;
}

[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#111827,#29265f 65%,#3730a3);
}

[data-testid="stSidebar"] * {
    color:#f8fafc !important;
}

.block-container {
    padding-top:2rem;
    padding-bottom:3.5rem;
    max-width:1280px;
}

[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4 {
    color:#1e2454;
    letter-spacing:-.025em;
}

[data-testid="stMain"] p {
    line-height:1.65;
}

.main-title {
    font-size:2.25rem;
    font-weight:850;
    color:#27245f;
    letter-spacing:-1.2px;
    margin-bottom:.2rem;
}

.sub-title {
    color:#667085;
    font-size:1rem;
    margin-bottom:1.2rem;
}

.hero {
    padding:2rem 2.2rem;
    border:1px solid rgba(255,255,255,.16);
    border-radius:24px;
    background:
        radial-gradient(circle at 90% 15%,rgba(173,164,255,.32),transparent 28%),
        linear-gradient(120deg,#20204f,#5149b8 65%,#655bd0);
    color:white;
    margin-bottom:1.5rem;
    box-shadow:0 18px 42px rgba(49,46,129,.16);
}

.hero h1 {
    color:white;
    font-size:clamp(1.8rem,3vw,2.4rem);
    font-weight:800;
    letter-spacing:-.04em;
    margin:0 0 .55rem 0;
}

.hero p {
    color:#e6e7ff;
    margin:0;
    font-size:1.02rem;
    max-width:760px;
    line-height:1.7;
}

.section-card {
    min-height:145px;
    background:linear-gradient(145deg,#fff,#fbfcff);
    border:1px solid var(--line);
    border-radius:20px;
    padding:1.35rem 1.45rem;
    margin:.4rem 0 1.1rem;
    box-shadow:0 8px 26px rgba(24,32,68,.055);
    transition:transform .18s ease,box-shadow .18s ease;
}

.section-card h3 {
    color:#292661;
    font-size:1.08rem;
    margin:.1rem 0 .55rem;
}

.section-card p {
    color:#58657a;
    font-size:.94rem;
    margin:0;
}

.week-card {
    background:linear-gradient(145deg,#fff,#fbfcff);
    border:1px solid var(--line);
    border-left:4px solid #625bd5;
    border-radius:18px;
    padding:1.1rem 1.3rem;
    margin:.7rem 0;
    box-shadow:0 8px 24px rgba(31,36,80,.055);
}

.week-task {
    padding:.45rem .2rem;
    color:#334155;
    border-bottom:1px solid #f1f3f9;
    line-height:1.6;
}

.week-task:last-child {
    border-bottom:0;
}

.week-heading {
    font-size:1.05rem;
    font-weight:750;
    color:#2e2b76;
    margin-bottom:.55rem;
}

.week-tag {
    display:inline-block;
    background:#efefff;
    color:#4f46a5;
    border-radius:999px;
    padding:.25rem .65rem;
    font-size:.75rem;
    font-weight:700;
    margin-right:.55rem;
}

.resource-chip {
    display:inline-block;
    background:#f0f7ff;
    color:#285b96;
    border:1px solid #dcecff;
    border-radius:8px;
    padding:.25rem .55rem;
    margin:.2rem .25rem .2rem 0;
    font-size:.82rem;
}

div[data-testid="stMetric"] {
    background:linear-gradient(145deg,#fff,#fbfcff);
    border:1px solid var(--line);
    padding:18px;
    border-radius:18px;
    box-shadow:0 7px 22px rgba(24,32,68,.05);
}

div[data-testid="stMetric"] label {
    color:#64748b;
    font-weight:600;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color:#292661;
    font-weight:800;
}

.stTabs [data-baseweb="tab-list"] {
    gap:6px;
    background:#e9eaf6;
    padding:6px;
    border:1px solid #e0e3f0;
    border-radius:16px;
}

.stTabs [data-baseweb="tab"] {
    border-radius:11px;
    padding:10px 16px;
    color:#535c75;
    font-weight:650;
}

.stTabs [aria-selected="true"] {
    background:white;
    color:#3730a3 !important;
    box-shadow:0 3px 10px rgba(24,32,68,.09);
}

.stButton > button,
.stDownloadButton > button {
    min-height:2.7rem;
    border-radius:12px;
    border:0;
    background:linear-gradient(90deg,#5149b8,#7066df);
    color:white;
    font-weight:700;
    padding:.7rem 1rem;
    box-shadow:0 5px 14px rgba(81,73,184,.16);
    transition:transform .16s ease,box-shadow .16s ease,background .16s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border:0;
    color:white;
    background:linear-gradient(90deg,#4338a8,#6257d2);
    transform:translateY(-1px);
    box-shadow:0 8px 18px rgba(81,73,184,.23);
}

.stButton > button:focus-visible,
.stDownloadButton > button:focus-visible {
    outline:3px solid #a5b4fc;
    outline-offset:2px;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] [data-baseweb="select"] {
    border-radius:10px;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background:#fff;
    color:#172033;
    border-color:#cbd5e1;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color:#7066df;
    box-shadow:0 0 0 3px rgba(112,102,223,.13);
}

[data-testid="stForm"] {
    background:rgba(255,255,255,.72);
    border:1px solid var(--line);
    border-radius:20px;
    padding:1.25rem 1.35rem;
}

[data-testid="stFileUploader"] {
    background:rgba(255,255,255,.82);
    border:1px dashed #aeb8df;
    border-radius:16px;
    padding:.8rem;
}

[data-testid="stExpander"] {
    background:rgba(255,255,255,.86);
    border:1px solid var(--line);
    border-radius:14px;
}

[data-testid="stAlert"] {
    border-radius:14px;
}

[data-testid="stDataFrame"] {
    border:1px solid var(--line);
    border-radius:14px;
    overflow:hidden;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background:rgba(255,255,255,.82);
    border:1px solid var(--line);
    border-radius:18px;
    box-shadow:0 8px 26px rgba(24,32,68,.055);
}

hr {
    border-color:#e7eaf3;
}

[data-testid="stPlotlyChart"] {
    background:#fff;
    border:1px solid var(--line);
    border-radius:18px;
    padding:.6rem;
    box-shadow:0 7px 22px rgba(24,32,68,.045);
}

@media (max-width:760px) {
    .block-container {
        padding-top:1.2rem;
        padding-left:1rem;
        padding-right:1rem;
    }

    .hero {
        padding:1.5rem;
        border-radius:19px;
    }

    .stTabs [data-baseweb="tab"] {
        padding:8px 10px;
        font-size:.85rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# ROADMAP DISPLAY
# Supports Day 1-7 and older Week-based roadmap formats
# ============================================================

def render_roadmap(roadmap_text):
    text = str(roadmap_text or "").strip()

    if not text:
        st.info("Roadmap is not available yet.")
        return

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    day_pattern = re.compile(
        r"^(?:#+\s*)?(?:\*\*)?(day\s*\d+[^:*\n]*)"
        r"(?:\*\*)?\s*[:—–-]?\s*(.*)$",
        re.I
    )

    week_pattern = re.compile(
        r"^(?:#+\s*)?(?:\*\*)?(week\s*\d+[^:*\n]*)"
        r"(?:\*\*)?\s*[:—–-]?\s*(.*)$",
        re.I
    )

    sections = []
    current = None
    section_type = None

    for line in lines:
        clean = line.lstrip("-•* ").strip()

        day_match = day_pattern.match(clean)
        week_match = week_pattern.match(clean)

        match = day_match or week_match

        if match:
            if current:
                sections.append(current)

            section_type = (
                "day" if day_match else "week"
            )

            current = {
                "title": match.group(1).strip(),
                "items": []
            }

            if match.group(2).strip():
                current["items"].append(
                    match.group(2).strip()
                )

        elif current:
            current["items"].append(clean)

    if current:
        sections.append(current)

    if not sections:
        st.markdown(text)
        return

    for index, section in enumerate(sections, start=1):
        title = section["title"]
        items = section["items"]

        topic = ""
        task = ""
        goal = ""
        other_items = []

        for item in items:
            item = re.sub(
                r"^[-*•]\s*",
                "",
                item
            ).strip()

            if item.lower().startswith("topic:"):
                topic = item.split(":", 1)[1].strip()

            elif item.lower().startswith("task:"):
                task = item.split(":", 1)[1].strip()

            elif item.lower().startswith("goal:"):
                goal = item.split(":", 1)[1].strip()

            elif item:
                other_items.append(item)

        with st.container(border=True):

            st.markdown(
                f"""
                <div class="week-heading">
                    <span class="week-tag">
                        {html.escape(title.upper())}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

            if topic:
                st.markdown(
                    f"**📚 Topic:** {topic}"
                )

            if task:
                st.markdown(
                    f"**🛠️ Task:** {task}"
                )

            if goal:
                st.markdown(
                    f"**🎯 Goal:** {goal}"
                )

            for item in other_items:
                st.markdown(
                    f'<div class="week-task">✓ &nbsp;{html.escape(item)}</div>',
                    unsafe_allow_html=True
                )


# ============================================================
# INTERVIEW DISPLAY
# ============================================================

def render_interview(interview_text):
    text = str(interview_text or "").strip()

    st.markdown("### 🎤 Interview Questions & Answers")

    if not text:
        st.info("Interview questions are not available.")
        return

    pattern = (
        r"(?:\d+\.\s*)?Question:\s*(.*?)"
        r"\s*Answer:\s*(.*?)(?="
        r"(?:\d+\.\s*)?Question:|$)"
    )

    pairs = re.findall(
        pattern,
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    if not pairs:
        st.markdown(text)
        return

    for index, (question, answer) in enumerate(
        pairs[:5],
        start=1
    ):

        question = question.strip()
        answer = answer.strip()

        with st.container(border=True):

            st.markdown(
                f"""
                <div class="week-heading">
                    <span class="week-tag">
                        QUESTION {index:02d}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"**❓ Question:** {question}"
            )

            st.markdown("---")

            st.markdown(
                f"**💡 Sample Answer:**"
            )

            st.markdown(answer)


def go_to_career_plan():
    st.session_state["page"] = "Career Plan"


# ============================================================
# AUTHENTICATION
# ============================================================

if "user_id" not in st.session_state:
    auth_page()
    st.stop()


username = st.session_state["username"]
user_id = st.session_state["user_id"]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🚀 CareerForge AI")
    st.caption(f"Signed in as {username}")

    page = st.radio(
        "Navigation",
        ["Dashboard", "Career Plan", "Resume Q&A", "Reports"],
        key="page"
    )

    st.divider()

    if st.button("Log out", width="stretch"):
        logout()


result = st.session_state.get("careerforge_result")

role = st.session_state.get(
    "careerforge_role",
    (result or {}).get("target_role", "")
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.markdown(
        f'<div class="hero">'
        f'<h1>Welcome back, {html.escape(username)} ✨</h1>'
        f'<p>Your personal space to understand your skills, '
        f'plan your studies, and move toward your dream role.</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    if not result:

        c1, c2, c3 = st.columns(3)

        c1.markdown(
            '<div class="section-card">'
            '<h3>📄 Resume insights</h3>'
            '<p>Upload your resume and discover your strengths.</p>'
            '</div>',
            unsafe_allow_html=True
        )

        c2.markdown(
            '<div class="section-card">'
            '<h3>📊 Skill analytics</h3>'
            '<p>See matched skills and priority skill gaps.</p>'
            '</div>',
            unsafe_allow_html=True
        )

        c3.markdown(
            '<div class="section-card">'
            '<h3>🗓️ Study roadmap</h3>'
            '<p>Get a week-by-week plan based on your goals.</p>'
            '</div>',
            unsafe_allow_html=True
        )

        st.button(
            "Start my career analysis →",
            type="primary",
            on_click=go_to_career_plan
        )

    show_dashboard(user_id, username, result)


# ============================================================
# CAREER PLAN
# ============================================================

elif page == "Career Plan":

    st.markdown(
        '<div class="hero">'
        '<h1>🚀 Build your career roadmap</h1>'
        '<p>Turn your resume and skills into a clear, '
        'personalized career journey.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">'
        'Upload your resume, select a role, and let your '
        'existing LangGraph agents analyze your next steps.'
        '</div>',
        unsafe_allow_html=True
    )

    uploaded_resume = st.file_uploader(
        "Resume (PDF, DOCX or TXT)",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_resume:

        try:
            resume_text = extract_resume(uploaded_resume)

            st.session_state["resume_text"] = resume_text
            st.session_state["resume_filename"] = uploaded_resume.name

            st.success(
                f"Resume extracted: {uploaded_resume.name} · "
                f"{len(resume_text.split())} words"
            )

            with st.expander("Preview extracted text"):
                st.text(resume_text[:3500])

        except Exception as exc:
            st.error(f"Resume extraction failed: {exc}")
            st.session_state.pop("resume_text", None)

    elif st.session_state.get("resume_text"):

        st.caption(
            "Using resume: "
            + st.session_state.get(
                "resume_filename",
                "uploaded resume"
            )
        )


    # --------------------------------------------------------
    # PROFILE FORM
    # --------------------------------------------------------

    st.markdown("### 🎓 Study & career profile")

    st.caption(
        "Enter your profile details to generate a personalized career roadmap."
    )

    with st.form("career_profile"):

        name = st.text_input(
            "Name",
            placeholder="Enter your name"
        )

        skills_text = st.text_area(
            "Current skills (comma-separated)",
            placeholder="Python, SQL, Git, REST APIs"
        )

        role_col, exp_col = st.columns(2)

        with role_col:

            role_options = sorted(
                JOB_DATA["roles"].keys()
            )

            target_role = st.selectbox(
                "Target job role",
                options=role_options,
                index=(
                    role_options.index(role)
                    if role in role_options
                    else 0
                )
            )

        with exp_col:

            experience = st.selectbox(
                "Experience level",
                ["Beginner", "Intermediate", "Advanced"]
            )

        submitted = st.form_submit_button(
            "✨ Generate personalized career plan",
            type="primary",
            width="stretch"
        )


    # --------------------------------------------------------
    # GENERATE CAREER PLAN
    # --------------------------------------------------------

    if submitted:

        current_skills = [
            item.strip()
            for item in skills_text.split(",")
            if item.strip()
        ]

        resume_text = st.session_state.get(
            "resume_text",
            ""
        )

        if resume_text:

            resume_lower = resume_text.lower()

            resume_skills = [
                skill
                for skill in JOB_DATA["roles"][target_role]
                if skill.lower() in resume_lower
            ]

            current_skills = list(
                dict.fromkeys(
                    current_skills + resume_skills
                )
            )

        if not current_skills and not resume_text:

            st.error(
                "Enter your skills or upload a resume first."
            )

        elif (
            not os.getenv("GROQ_API_KEY")
            and not os.getenv("OPENAI_API_KEY")
        ):

            st.error(
                "Add at least one valid model API key to your .env file."
            )

        else:

            initial_state = {
                "name": name.strip() or "Learner",
                "current_skills": current_skills,
                "target_role": target_role,
                "experience": experience,
                "resume_text": resume_text,

                # Existing compatibility fields retained
                "education_level": "",
                "degree": "",
                "specialization": "",
                "institution": "",
                "graduation_year": "",
                "certifications": "",
                "projects": "",
                "career_interests": "",
                "weekly_study_hours": "",
                "learning_preference": "",
            }

            try:

                generated_result = dict(initial_state)

                with st.status(
                    "Preparing your career plan...",
                    expanded=True
                ) as status:

                    for update in build_workflow().stream(
                        initial_state,
                        stream_mode="updates"
                    ):

                        for node_name, node_result in update.items():

                            generated_result.update(
                                node_result or {}
                            )

                            if node_name == "mcp_research":

                                status.update(
                                    label="Matching your skills with the role...",
                                    state="running"
                                )

                            elif node_name == "career_plan":

                                status.update(
                                    label="Generating your career plan...",
                                    state="running"
                                )

                    status.update(
                        label="Career plan completed",
                        state="complete",
                        expanded=False
                    )

                generated_result["target_role"] = target_role
                generated_result["current_skills"] = current_skills
                generated_result["name"] = name.strip() or "Learner"
                generated_result["experience"] = experience

                st.session_state["careerforge_result"] = generated_result
                st.session_state["careerforge_role"] = target_role

                save_analysis(
                    user_id,
                    target_role,
                    generated_result
                )

                st.success(
                    "Career plan generated and saved to your account."
                )

            except Exception as exc:

                st.error("Career plan generation failed.")
                st.exception(exc)


    # --------------------------------------------------------
    # DISPLAY CAREER ANALYSIS
    # --------------------------------------------------------

    result = st.session_state.get(
        "careerforge_result"
    )

    if result:

        st.markdown(
            f'<div class="hero">'
            f'<h1>✨ Your career analysis</h1>'
            f'<p>A personalized action plan for '
            f'{html.escape(result.get("target_role", role or "your target role"))} '
            f'— explore each section below.</p>'
            f'</div>',
            unsafe_allow_html=True
        )

        comparison = result.get(
            "mcp_skill_comparison",
            {}
        ) or {}

        matched = comparison.get(
            "matched",
            []
        ) or []

        missing = comparison.get(
            "missing",
            []
        ) or []

        required = result.get(
            "required_skills",
            []
        ) or []

        matched_lower = {
            str(skill).casefold()
            for skill in matched
        }
        missing_lower = {
            str(skill).casefold()
            for skill in missing
        }
        skills_for_table = required or list(
            dict.fromkeys(matched + missing)
        )
        skill_status_rows = [
            {
                "Skill": skill,
                "Status": (
                    "Missing"
                    if str(skill).casefold() in missing_lower
                    or str(skill).casefold() not in matched_lower
                    else "Not missing"
                ),
            }
            for skill in skills_for_table
        ]

        coverage = (
            round(
                len(matched) / len(required) * 100
            )
            if required
            else 0
        )

        m1, m2, m3 = st.columns(3)

        m1.metric("Skills matched", len(matched))
        m2.metric("Skills to learn", len(missing))
        m3.metric("Skill coverage", f"{coverage}%")


        # ----------------------------------------------------
        # PIE CHART AND BAR CHART - KEPT
        # ----------------------------------------------------

        if required:

            chart_left, chart_right = st.columns(
                [1, 1.35]
            )

            with chart_left:

                skill_pie = pd.DataFrame({
                    "Skill status": [
                        "Matched",
                        "To learn"
                    ],
                    "Count": [
                        len(matched),
                        len(missing)
                    ]
                })

                pie = px.pie(
                    skill_pie,
                    names="Skill status",
                    values="Count",
                    hole=0.62,
                    title="Your skill readiness"
                )

                pie.update_layout(
                    template="plotly_white",
                    height=330,
                    margin=dict(
                        t=55,
                        b=10,
                        l=10,
                        r=10
                    ),
                    legend_title_text=""
                )

                st.plotly_chart(
                    pie,
                    width="stretch"
                )

            with chart_right:

                skill_rows = [
                    {
                        "Skill": skill,
                        "Status": (
                            "Matched"
                            if str(skill).casefold() in matched_lower
                            else "To learn"
                        )
                    }
                    for skill in required
                ]

                bar = px.bar(
                    pd.DataFrame(skill_rows),
                    x="Skill",
                    color="Status",
                    title="Role skills at a glance"
                )

                bar.update_layout(
                    template="plotly_white",
                    height=330,
                    margin=dict(
                        t=55,
                        b=55,
                        l=10,
                        r=10
                    ),
                    xaxis_title="",
                    yaxis_title="",
                    legend_title_text=""
                )

                bar.update_xaxes(
                    tickangle=-35
                )

                st.plotly_chart(
                    bar,
                    width="stretch"
                )


        # ----------------------------------------------------
        # TABS
        # ----------------------------------------------------

        tabs = st.tabs([
            "👤 Profile",
            "🎯 Skill gaps",
            "🗓️ Roadmap",
            "💬 Interview",
            "📄 Final report"
        ])


        # PROFILE TAB
        with tabs[0]:

            with st.container(border=True):

                st.markdown("### Profile overview")

                st.markdown(
                    result.get(
                        "profile_analysis",
                        "Not available."
                    )
                )

            st.markdown("### 👤 Candidate details")

            profile_items = [
                (
                    "Name",
                    result.get(
                        "name",
                        "Not specified"
                    )
                ),
                (
                    "Current skills",
                    ", ".join(
                        result.get(
                            "current_skills",
                            []
                        )
                    )
                    if isinstance(
                        result.get("current_skills"),
                        list
                    )
                    else result.get(
                        "current_skills",
                        "Not specified"
                    )
                ),
                (
                    "Target job role",
                    result.get(
                        "target_role",
                        "Not specified"
                    )
                ),
                (
                    "Education",
                    result.get(
                        "education_level",
                        "Not specified"
                    )
                ),
                (
                    "Experience level",
                    result.get(
                        "experience",
                        "Not specified"
                    )
                ),
            ]

            profile_cols = st.columns(3)

            for idx, (label, value) in enumerate(
                profile_items
            ):

                with profile_cols[idx % 3]:

                    st.markdown(
                        f"""
                        <div class="section-card">
                            <div style="color:#64748b;font-size:.8rem">
                                {html.escape(str(label))}
                            </div>
                            <div style="font-weight:750;color:#27245f">
                                {html.escape(str(value or "Not specified"))}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


        # SKILL GAPS TAB
        with tabs[1]:

            with st.container(border=True):

                st.markdown("### Your skill gap overview")

                st.markdown(
                    result.get(
                        "skill_gap_analysis",
                        "Not available."
                    )
                )

            st.markdown("#### Skill checklist")
            st.caption(
                "Not missing means the skill is already matched to your profile. "
                "Missing skills are areas to focus on next."
            )
            if skill_status_rows:
                st.dataframe(
                    pd.DataFrame(skill_status_rows),
                    width="stretch",
                    hide_index=True
                )
            else:
                st.caption("No required skills are available for this analysis.")


        # ROADMAP TAB
        with tabs[2]:

            st.markdown("### Your learning journey")

            st.caption(
                "Follow the 7 days in order. Each step moves you "
                "closer to your target role."
            )

            render_roadmap(
                result.get(
                    "learning_roadmap",
                    ""
                )
            )

            resources = result.get(
                "learning_resources",
                []
            ) or []

            if resources:

                with st.expander(
                    "📚 Recommended resources"
                ):

                    for resource in resources:
                        st.markdown(f"- {resource}")


        # INTERVIEW TAB
        with tabs[3]:

            st.markdown("### Interview practice")

            st.caption(
                "Prepare for your target role with questions "
                "and sample answers."
            )

            interview_text = result.get(
                "interview_preparation",
                ""
            )

            render_interview(
                interview_text
            )


        # FINAL REPORT TAB
        with tabs[4]:

            with st.container(border=True):

                st.markdown("### Career summary")

                st.markdown(
                    result.get(
                        "final_report",
                        "Not available."
                    )
                )

            st.download_button(
                "⬇️ Download report",
                markdown_report(
                    result,
                    role or "Career Plan"
                ),
                "careerforge_report.md",
                "text/markdown",
                width="stretch"
            )


        with st.expander(
            "View technical research details"
        ):

            st.json(
                result.get(
                    "mcp_skill_comparison",
                    {}
                )
            )

            st.json(
                result.get(
                    "learning_resources",
                    []
                )
            )


# ============================================================
# RESUME Q&A
# ============================================================

elif page == "Resume Q&A":

    st.markdown(
        '<div class="hero">'
        '<h1>Resume interview coach</h1>'
        '<p>Ask a question and get a concise answer grounded in the '
        'experience and skills in your uploaded resume.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.get("resume_text"):

        st.warning(
            "Upload a resume to unlock personalized interview answers."
        )
        st.button(
            "Go to career plan and upload a resume →",
            type="primary",
            on_click=go_to_career_plan
        )

    else:

        with st.form(
            "resume_question_form",
            clear_on_submit=True
        ):

            question = st.text_input(
                "Ask a question about your resume"
            )

            submitted = st.form_submit_button(
                "Get answer"
            )

        if submitted and question.strip():

            retrieved = retrieve_resume_context(
                st.session_state["resume_text"],
                question,
                top_k=2
            )

            retrieved = str(retrieved)[:1800]

            q = question.lower().strip()

            is_intro = any(
                phrase in q
                for phrase in [
                    "introduce yourself",
                    "tell me about yourself",
                    "give me an introduction",
                    "self introduction",
                    "short intro"
                ]
            )

            if is_intro:

                system_prompt = """
Answer as a candidate speaking in an interview.

Use only the resume excerpts.
Give a natural, short spoken introduction.
Mention relevant skills and experience.
Maximum 80 words.
Return plain text only.
"""

            else:

                system_prompt = """
You are answering a question about a resume.

Use only the resume excerpts provided.
Answer directly and clearly.
Maximum 60 words.
For project questions, use 2-3 sentences.
Do not repeat the question.
If the answer is missing from the resume, say:
This information was not found in the resume.

Return plain text only.
"""

            with st.spinner(
                "Preparing your answer..."
            ):

                answer = run_agent(
                    "open",
                    system_prompt,
                    f"Resume excerpts:\n{retrieved}\n\nQuestion: {question}",
                    json_mode=False,
                )

            with st.container(border=True):
                st.markdown("### Suggested answer")
                st.markdown(answer)


# ============================================================
# REPORTS
# ============================================================

elif page == "Reports":

    st.markdown(
        '<div class="hero">'
        '<h1>Your career reports</h1>'
        '<p>Take your personalized career plan with you. Download a '
        'readable report or export your skill checklist.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    if not result:

        st.info(
            "Your reports will appear here after you generate a career plan."
        )
        st.button(
            "Create my career plan →",
            type="primary",
            on_click=go_to_career_plan
        )

    else:

        role = result.get(
            "target_role",
            role or "Career Plan"
        )

        st.markdown(
            f'<div class="section-card">'
            f'<h3>Ready for your next step</h3>'
            f'<p>Your latest plan is for <strong>{html.escape(str(role))}</strong>. '
            f'Choose a format below to save or share it.</p>'
            f'</div>',
            unsafe_allow_html=True
        )

        report_columns = st.columns(3, gap="medium")
        with report_columns[0]:
            st.download_button(
                "Download Markdown report",
                markdown_report(result, role),
                "careerforge_report.md",
                "text/markdown",
                width="stretch"
            )

        with report_columns[1]:
            st.download_button(
                "Download PDF report",
                pdf_report(result, role),
                "careerforge_report.pdf",
                "application/pdf",
                width="stretch"
            )

        comparison = result.get(
            "mcp_skill_comparison",
            {}
        ) or {}

        with report_columns[2]:
            st.download_button(
                "Download skills CSV",
                skills_csv(
                    result.get("required_skills", []),
                    comparison.get("matched", []),
                    comparison.get("missing", [])
                ),
                "careerforge_skills.csv",
                "text/csv",
                width="stretch"
            )
