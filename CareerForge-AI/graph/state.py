from typing import TypedDict


class CareerState(TypedDict, total=False):
    name: str
    current_skills: list[str]
    target_role: str
    experience: str
    education_level: str
    degree: str
    specialization: str
    institution: str
    graduation_year: str
    certifications: str
    projects: str
    career_interests: str
    weekly_study_hours: str
    learning_preference: str
    resume_text: str
    profile_analysis: str
    required_skills: list[str]
    mcp_skill_comparison: dict
    learning_resources: list
    skill_gap_analysis: str
    learning_roadmap: str
    interview_preparation: str
    final_report: str
