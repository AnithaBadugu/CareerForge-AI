import pandas as pd
import plotly.express as px
import streamlit as st

from database import get_analysis, history_for_user


def show_dashboard(user_id, username, result=None):
    st.markdown("### Progress overview")
    st.caption(
        f"Your latest skill analysis and saved career plans, {username}."
    )

    if result:
        comparison = result.get("mcp_skill_comparison", {}) or {}
        matched = comparison.get("matched", []) or []
        missing = comparison.get("missing", []) or []
        required = result.get("required_skills", []) or []
        total = len(required)
        coverage = round(len(matched) / total * 100) if total else 0

        metric_columns = st.columns(3)
        metric_columns[0].metric("Role skills", total)
        metric_columns[1].metric("Skills matched", len(matched))
        metric_columns[2].metric("Skill coverage", f"{coverage}%")

        study_fields = [
            ("Education", result.get("education_level")),
            ("Degree", result.get("degree")),
            ("Graduation", result.get("graduation_year")),
            ("Study hours / week", result.get("weekly_study_hours")),
        ]
        visible_study = [
            (label, value)
            for label, value in study_fields
            if value and value != "Not specified"
        ]
        if visible_study:
            st.markdown("#### Your study profile")
            study_columns = st.columns(min(4, len(visible_study)))
            for index, (label, value) in enumerate(visible_study):
                study_columns[index].metric(label, value)

        if required:
            matched_lower = {skill.lower() for skill in matched}
            status_by_skill = [
                "Matched" if skill.lower() in matched_lower else "To learn"
                for skill in required
            ]
            skills_frame = pd.DataFrame(
                {"Skill": required, "Status": status_by_skill}
            )

            st.markdown("#### Skills at a glance")
            chart_column, coverage_column = st.columns(2, gap="large")
            with chart_column:
                bar = px.bar(
                    skills_frame,
                    x="Skill",
                    color="Status",
                    title="Skills for your target role",
                    color_discrete_map={
                        "Matched": "#16a37a",
                        "To learn": "#f0a44b",
                    },
                )
                bar.update_layout(
                    template="plotly_white",
                    height=360,
                    font_family="Inter",
                    margin=dict(t=60, b=55, l=12, r=12),
                    xaxis_title="",
                    yaxis_title="",
                    legend_title_text="",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                bar.update_xaxes(tickangle=-30, gridcolor="#eef1f7")
                bar.update_yaxes(gridcolor="#eef1f7")
                st.plotly_chart(bar, width="stretch")

            with coverage_column:
                coverage_frame = pd.DataFrame(
                    {
                        "Status": ["Matched", "Missing"],
                        "Count": [len(matched), len(missing)],
                    }
                )
                pie = px.pie(
                    coverage_frame,
                    names="Status",
                    values="Count",
                    hole=0.62,
                    title="Your skill coverage",
                    color="Status",
                    color_discrete_map={
                        "Matched": "#16a37a",
                        "Missing": "#f0a44b",
                    },
                )
                pie.update_layout(
                    template="plotly_white",
                    height=360,
                    font_family="Inter",
                    margin=dict(t=60, b=12, l=12, r=12),
                    legend_title_text="",
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(pie, width="stretch")

        if missing:
            st.info("Focus skills for your next study session: " + ", ".join(missing))

    st.markdown("### Saved career plans")
    rows = history_for_user(user_id)
    if not rows:
        st.caption(
            "Your saved plans will appear here after you complete a career analysis."
        )
        return

    history = pd.DataFrame([dict(row) for row in rows])
    history = history.rename(
        columns={
            "id": "Plan",
            "target_role": "Target role",
            "created_at": "Created",
        }
    )
    st.dataframe(history, width="stretch", hide_index=True)

    analysis_ids = [row["id"] for row in rows]
    selected_id = st.selectbox(
        "Open a saved plan",
        analysis_ids,
        format_func=lambda analysis_id: next(
            f"Plan #{row['id']} · {row['target_role']} · {row['created_at']}"
            for row in rows
            if row["id"] == analysis_id
        ),
    )
    if st.button("Open selected plan", type="primary"):
        saved = get_analysis(user_id, selected_id)
        if saved:
            st.session_state["careerforge_result"] = saved["result"]
            st.session_state["careerforge_role"] = saved["target_role"]
            st.session_state["page"] = "Career Plan"
            st.rerun()
