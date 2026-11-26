import streamlit as st
import pandas as pd
import plotly.express as px
from database import history_for_user, get_analysis

def show_dashboard(user_id, username, result=None):
    st.title("Your Career Dashboard")
    st.caption(f"Welcome, {username} — track your preparation for your target role.")
    if result:
        comparison = result.get("mcp_skill_comparison", {}) or {}
        matched = comparison.get("matched", []) or []
        missing = comparison.get("missing", []) or []
        required = result.get("required_skills", []) or []
        total = len(required)
        coverage = round(len(matched) / total * 100) if total else 0
        a,b,c = st.columns(3)
        a.metric("Required skills", total)
        b.metric("Matched skills", len(matched))
        c.metric("Skill coverage", f"{coverage}%")
        # Show learner study details from the latest generated profile.
        study_fields = [
            ("Education", result.get("education_level")),
            ("Degree", result.get("degree")),
            ("Graduation", result.get("graduation_year")),
            ("Study hours/week", result.get("weekly_study_hours")),
        ]
        visible_study = [(label, value) for label, value in study_fields if value and value != "Not specified"]
        if visible_study:
            st.subheader("Study profile")
            study_cols = st.columns(min(4, len(visible_study)))
            for index, (label, value) in enumerate(visible_study):
                study_cols[index].metric(label, value)
        if required:
            df = pd.DataFrame({"Skill": required, "Status": ["Matched" if s.lower() in {m.lower() for m in matched} else "Gap" for s in required]})
            st.subheader("Skills overview")
            fig = px.bar(df, x="Skill", color="Status", title="Required skills: matched vs skill gaps")
            fig.update_layout(template="plotly_white", height=360, legend_title_text="Status")
            st.plotly_chart(fig, use_container_width=True)
            gap_df = pd.DataFrame({"Status": ["Matched", "Missing"], "Count": [len(matched), len(missing)]})
            fig2 = px.pie(gap_df, names="Status", values="Count", hole=0.58, title="Skill coverage")
            fig2.update_layout(template="plotly_white", height=330, margin=dict(t=55, b=10, l=10, r=10), legend_title_text="")
            st.plotly_chart(fig2, use_container_width=True)
        if missing:
            st.info("Priority skills to learn: " + ", ".join(missing))
    st.subheader("Analysis history")
    rows = history_for_user(user_id)
    if not rows:
        st.caption("Your saved career plans will appear here.")
        return
    hist = pd.DataFrame([dict(row) for row in rows])
    st.dataframe(hist.rename(columns={"id":"Analysis ID", "target_role":"Target role", "created_at":"Created"}), use_container_width=True, hide_index=True)
    ids = [row["id"] for row in rows]
    selected = st.selectbox("Open a saved analysis", ids, format_func=lambda i: next(f"#{row['id']} · {row['target_role']} · {row['created_at']}" for row in rows if row['id']==i))
    if st.button("Load selected analysis"):
        saved = get_analysis(user_id, selected)
        if saved:
            st.session_state["careerforge_result"] = saved["result"]
            st.session_state["careerforge_role"] = saved["target_role"]
            st.session_state["page"] = "Career Plan"
            st.rerun()
