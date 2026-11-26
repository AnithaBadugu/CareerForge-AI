
import json
import re
from pathlib import Path

from langgraph.graph import END, START, StateGraph

from agents.agent_factory import run_agent
from graph.state import CareerState
from mcp_server.client import get_role_context


ROOT = Path(__file__).resolve().parents[1]

with (ROOT / "data" / "job_roles.json").open(
    "r", encoding="utf-8"
) as f:
    JOB_DATA = json.load(f)


def _as_skill_list(value) -> list[str]:
    """Convert skill data into a clean list of strings."""

    if value is None:
        return []

    if isinstance(value, dict):
        value = value.get("skills", [])

    if isinstance(value, str):
        value = re.split(r"[,;\n]", value)

    if not isinstance(value, (list, tuple, set)):
        return []

    skills = []

    for item in value:
        skill = str(item).strip()

        if skill and skill not in skills:
            skills.append(skill)

    return skills


def _get_role_skills(target_role: str) -> list[str]:
    """Get required skills from job_roles.json."""

    role_info = JOB_DATA.get(
        "roles", {}
    ).get(target_role, {})

    if isinstance(role_info, dict):
        role_skills = role_info.get(
            "skills", []
        )

    elif isinstance(role_info, list):
        role_skills = role_info

    else:
        role_skills = []

    return _as_skill_list(role_skills)


def _resume_excerpt(
    text: str,
    limit: int = 450
) -> str:
    if not text:
        return "No resume provided."

    words = text.split()

    return " ".join(words[:limit])


def mcp_research_node(state: CareerState) -> dict:
    target_role = state.get(
        "target_role", ""
    )

    current_skills = _as_skill_list(
        state.get("current_skills", [])
    )

    role_context = {}

    # Get role information from MCP
    try:
        role_context = get_role_context(
            target_role,
            current_skills
        )

        if not isinstance(role_context, dict):
            role_context = {}

    except Exception:
        role_context = {}

    # Get required skills from MCP or local data
    required_skills = _as_skill_list(
        role_context.get("required_skills")
        or _get_role_skills(target_role)
    )

    # Compare current skills with required skills
    current_lower = {
        skill.lower()
        for skill in current_skills
    }

    matched = [
        skill
        for skill in required_skills
        if skill.lower() in current_lower
    ]

    missing = [
        skill
        for skill in required_skills
        if skill.lower() not in current_lower
    ]

    comparison = role_context.get(
        "comparison", ""
    )

    learning_resources = role_context.get(
        "learning_resources", []
    )

    if not isinstance(learning_resources, list):
        learning_resources = []

    return {
        "required_skills": required_skills,
        "comparison": comparison,
        "mcp_skill_comparison": {
            "matched": matched,
            "missing": missing,
        },
        "learning_resources": learning_resources,
    }


def career_plan_node(state: CareerState) -> dict:
    name = state.get(
        "name", "Candidate"
    )

    target_role = state.get(
        "target_role", ""
    )

    current_skills = _as_skill_list(
        state.get("current_skills", [])
    )

    experience = state.get(
        "experience", "Beginner"
    )

    resume_text = state.get(
        "resume_text", ""
    )

    required_skills = _as_skill_list(
        state.get("required_skills", [])
    )

    comparison = state.get(
        "comparison", ""
    )

    learning_resources = state.get(
        "learning_resources", []
    )

    skill_comparison = state.get(
        "mcp_skill_comparison", {}
    ) or {}

    matched_skills = skill_comparison.get(
        "matched", []
    )

    missing_skills = skill_comparison.get(
        "missing", []
    )

    resume_excerpt = _resume_excerpt(
        resume_text,
        limit=450
    )

    system_prompt = """
You are a professional career guidance assistant.

Create a practical, personalized career plan.

Return ONLY valid JSON.
Do not use Markdown code fences.
Do not add extra AI-generated fields.

The JSON must contain exactly these 5 keys:

{
  "profile_analysis": "...",
  "skill_gap_analysis": "...",
  "learning_roadmap": "...",
  "interview_preparation": "...",
  "final_report": "..."
}

GENERAL RULES:

1. Use simple, clear English.

2. Do not invent experience, achievements,
   qualifications, or skills.

3. Do not include education, degree, university,
   college, or unnecessary profile fields.

4. Do not create separate JSON fields for skills,
   experience, education, or qualifications.

5. Use the candidate's actual current skills,
   experience level, target role, and resume.

PROFILE ANALYSIS:

6. profile_analysis must contain at least
   5 meaningful lines.

7. Each line must contain a complete and useful
   sentence about the candidate.

8. Discuss current skills, experience level,
   strengths, career goal, and suitability
   for the target role.

SKILL GAP ANALYSIS:

9. skill_gap_analysis must contain at least
   5 meaningful lines.

10. Explain current skills, required skills,
    matched skills, missing skills, and
    important skills to improve.

11. Mention which skills should be prioritized
    first and why.

LEARNING ROADMAP:

12. learning_roadmap must contain exactly
    7 days.

Use this exact format:

Day 1
Topic: ...
Task: ...
Goal: ...

Day 2
Topic: ...
Task: ...
Goal: ...

Continue until Day 7.

13. Keep each item on a separate line.

14. Use practical, beginner-friendly tasks.

15. Make the roadmap suitable for the candidate's
    current skills and experience.

INTERVIEW PREPARATION:

16. interview_preparation must contain exactly
    5 interview questions WITH sample answers.

Use this exact format:

1. Question: ...
Answer: ...

2. Question: ...
Answer: ...

Continue until Question 5.

17. Each question and answer must be on
    separate lines.

18. Add a blank line between each question
    and answer pair.

19. Do not provide questions without answers.

FINAL REPORT:

20. final_report must contain at least
    5 meaningful lines.

21. Each line must be a complete, useful sentence.

22. Summarize the candidate's career goal,
    current readiness, major skill gaps,
    learning priorities, and next steps.

23. Do not repeat the same sentence to reach
    the minimum line count.

24. Keep the report concise but informative.

JSON RULES:

25. Use newline characters inside string values
    wherever separate lines are required.

26. Escape quotation marks correctly.

27. Ensure the JSON is valid and complete.
"""

    user_prompt = f"""
Candidate name: {name}

Target role: {target_role}

Current skills: {current_skills}

Experience level: {experience}

Required skills for the role: {required_skills}

Matched skills: {matched_skills}

Missing skills: {missing_skills}

Skill comparison: {comparison}

Learning resources: {learning_resources}

Resume excerpt:
{resume_excerpt}

Create the career plan using the exact
5-key JSON structure.

Important requirements:

- profile_analysis must have at least 5 lines.
- skill_gap_analysis must have at least 5 lines.
- final_report must have at least 5 lines.
- learning_roadmap must contain exactly 7 days.
- interview_preparation must contain exactly
  5 questions with sample answers.
- Put each roadmap item on a separate line.
- Put each interview question and answer
  on separate lines.
- Do not include education, degree,
  university, or additional AI-generated fields.
"""

    content = run_agent(
        "open",
        system_prompt,
        user_prompt,
        json_mode=True
    )

    content = content.strip()

    # Remove Markdown code fences if returned
    content = re.sub(
        r"^```(?:json)?\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = re.sub(
        r"\s*```$",
        "",
        content
    )

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        # Try to extract the JSON object
        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1:
            result = json.loads(
                content[start:end + 1]
            )

        else:
            raise ValueError(
                "The AI returned invalid JSON. "
                "Please try generating the career plan again."
            )

    expected_keys = [
        "profile_analysis",
        "skill_gap_analysis",
        "learning_roadmap",
        "interview_preparation",
        "final_report",
    ]

    # Keep the five AI-generated fields
    cleaned_result = {}

    for key in expected_keys:
        value = result.get(key, "")

        if isinstance(value, list):
            value = "\n".join(
                str(item)
                for item in value
            )

        elif not isinstance(value, str):
            value = str(value)

        cleaned_result[key] = value.strip()

    # Preserve skill data for the dashboard
    cleaned_result["required_skills"] = (
        required_skills
    )

    cleaned_result["mcp_skill_comparison"] = {
        "matched": matched_skills,
        "missing": missing_skills,
    }

    cleaned_result["comparison"] = comparison

    cleaned_result["learning_resources"] = (
        learning_resources
    )

    return cleaned_result


def build_workflow():
    workflow = StateGraph(CareerState)

    workflow.add_node(
        "mcp_research",
        mcp_research_node
    )

    workflow.add_node(
        "career_plan",
        career_plan_node
    )

    workflow.add_edge(
        START,
        "mcp_research"
    )

    workflow.add_edge(
        "mcp_research",
        "career_plan"
    )

    workflow.add_edge(
        "career_plan",
        END
    )

    return workflow.compile()
