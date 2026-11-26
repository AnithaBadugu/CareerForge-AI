import io, csv, json
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def markdown_report(result, role):
    sections = [("Career Report", f"**Target role:** {role}"),
        ("Career Profile", result.get("profile_analysis", "")),
        ("Skill Gap Analysis", result.get("skill_gap_analysis", "")),
        ("Learning Roadmap", result.get("learning_roadmap", "")),
        ("Interview Preparation", result.get("interview_preparation", "")),
        ("Final Report", result.get("final_report", ""))]
    text = []
    for heading, body in sections:
        text.extend([f"# {heading}", "", str(body or "Not available"), ""])
    return "\n".join(text)

def pdf_report(result, role):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
    styles = getSampleStyleSheet()
    story = [Paragraph("CareerForge AI Career Report", styles["Title"]), Spacer(1, 12),
             Paragraph("Target role: " + escape(str(role)), styles["Heading2"]), Spacer(1, 14)]
    fields = [("Career Profile", "profile_analysis"), ("Skill Gap Analysis", "skill_gap_analysis"),
              ("Learning Roadmap", "learning_roadmap"), ("Interview Preparation", "interview_preparation"),
              ("Final Career Report", "final_report")]
    for title, key in fields:
        story.append(Paragraph(escape(title), styles["Heading2"]))
        raw = str(result.get(key, "Not available") or "Not available")
        # Keep report text safe for ReportLab's paragraph parser.
        raw = escape(raw).replace("\n", "<br/>")
        story.append(Paragraph(raw, styles["BodyText"]))
        story.append(Spacer(1, 12))
    doc.build(story)
    buffer.seek(0)
    return buffer

def skills_csv(required, matched, missing):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Skill", "Status"])
    matched_set = {x.lower() for x in matched}
    for skill in required:
        writer.writerow([skill, "Matched" if skill.lower() in matched_set else "Gap"])
    return buffer.getvalue().encode("utf-8-sig")
