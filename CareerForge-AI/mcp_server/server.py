import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CareerForge Career Tools")
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "job_roles.json"


def load_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@mcp.tool()
def get_job_skills(role: str) -> str:
    """Return the required skill list for a supported job role."""
    roles = load_data()["roles"]
    matched_role = next((key for key in roles if key.lower() == role.lower()), None)
    if not matched_role:
        return json.dumps({"error": f"Unsupported role: {role}", "available_roles": list(roles)})
    return json.dumps({"role": matched_role, "required_skills": roles[matched_role]})


@mcp.tool()
def calculate_skill_gap(current_skills: list[str], required_skills: list[str]) -> str:
    """Compare current skills with role requirements and return matched and missing skills."""
    current = {skill.strip().lower(): skill.strip() for skill in current_skills if skill.strip()}
    required = [skill for skill in required_skills if skill.strip()]
    matched = [skill for skill in required if skill.lower() in current]
    missing = [skill for skill in required if skill.lower() not in current]
    return json.dumps({
        "matched": matched,
        "missing": missing,
        "required_count": len(required),
        "matched_count": len(matched),
    })


@mcp.tool()
def get_learning_resources(skills: list[str]) -> str:
    """Return simple learning-focus suggestions for a list of skills."""
    suggestions = [
        {
            "skill": skill,
            "learning_focus": f"Study the fundamentals of {skill}, complete a guided exercise, "
                              f"and build a small practical example using {skill}.",
        }
        for skill in skills
    ]
    return json.dumps(suggestions)


if __name__ == "__main__":
    mcp.run(transport="stdio")
