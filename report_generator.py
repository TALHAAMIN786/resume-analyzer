"""
report_generator.py — Generate downloadable PDF reports
Phase 5: Export ATS analysis + job match results as PDF
"""

import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", fontSize=22, leading=26, spaceAfter=4,
        textColor=colors.HexColor("#1a1a2e"), fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle", fontSize=10, leading=14,
        textColor=colors.HexColor("#666666"), spaceAfter=18
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader", fontSize=14, leading=18, spaceBefore=16, spaceAfter=8,
        textColor=colors.HexColor("#4F8BF9"), fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="Body", fontSize=10, leading=15, textColor=colors.HexColor("#222222")
    ))
    styles.add(ParagraphStyle(
        name="BulletItem", fontSize=10, leading=15, leftIndent=14,
        textColor=colors.HexColor("#222222")
    ))
    styles.add(ParagraphStyle(
        name="ScoreBig", fontSize=36, leading=40, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#4F8BF9")
    ))
    return styles


def _skill_list(skills, empty_text="None"):
    return ", ".join(skills) if skills else empty_text


def generate_pdf_report(analysis: dict, match: dict = None, resume_name: str = "Resume") -> bytes:
    """
    Build a PDF report from ATS analysis (and optional job match) data.
    Returns raw PDF bytes, ready for st.download_button.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch
    )
    styles = _build_styles()
    story = []

    # ── Title ──
    story.append(Paragraph("AI Resume Analysis Report", styles["ReportTitle"]))
    story.append(Paragraph(
        f"{resume_name} &nbsp;&middot;&nbsp; Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles["ReportSubtitle"]
    ))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#dddddd")))

    # ── ATS Score ──
    score = analysis.get("ats_score", 0)
    verdict = analysis.get("overall_verdict", "—")

    story.append(Paragraph("ATS Score", styles["SectionHeader"]))
    score_table = Table(
        [[Paragraph(f"{score}/100", styles["ScoreBig"]), Paragraph(verdict, styles["Body"])]],
        colWidths=[1.4 * inch, 5.4 * inch]
    )
    score_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(score_table)

    # ── Score Breakdown ──
    breakdown = analysis.get("score_breakdown", {})
    max_scores = {"formatting": 20, "keywords": 25, "experience": 25, "skills": 20, "education": 10}
    if breakdown:
        story.append(Paragraph("Score Breakdown", styles["SectionHeader"]))
        rows = [["Category", "Score"]]
        for key, max_val in max_scores.items():
            rows.append([key.capitalize(), f"{breakdown.get(key, 0)} / {max_val}"])
        t = Table(rows, colWidths=[3 * inch, 2 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F8BF9")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
        ]))
        story.append(t)

    # ── Skills ──
    story.append(Paragraph("Skills", styles["SectionHeader"]))
    story.append(Paragraph(f"<b>Detected:</b> {_skill_list(analysis.get('detected_skills', []))}", styles["Body"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Missing:</b> {_skill_list(analysis.get('missing_skills', []), 'None flagged')}", styles["Body"]))

    # ── Weak Phrases ──
    weak_phrases = analysis.get("weak_phrases", [])
    if weak_phrases:
        story.append(Paragraph("Weak Language &rarr; Suggested Fixes", styles["SectionHeader"]))
        for wp in weak_phrases:
            story.append(Paragraph(
                f"<font color='#c0392b'>{wp.get('original','')}</font> &rarr; "
                f"<font color='#1e8449'>{wp.get('suggestion','')}</font>",
                styles["BulletItem"]
            ))
            story.append(Spacer(1, 3))

    # ── Section Feedback ──
    section_feedback = analysis.get("section_feedback", {})
    if section_feedback:
        story.append(Paragraph("Section-by-Section Feedback", styles["SectionHeader"]))
        for section, feedback in section_feedback.items():
            story.append(Paragraph(f"<b>{section.capitalize()}:</b> {feedback}", styles["Body"]))
            story.append(Spacer(1, 4))

    # ── Strengths / Fixes ──
    strengths = analysis.get("top_strengths", [])
    fixes = analysis.get("critical_fixes", [])
    if strengths:
        story.append(Paragraph("Top Strengths", styles["SectionHeader"]))
        for s in strengths:
            story.append(Paragraph(f"&bull; {s}", styles["BulletItem"]))
    if fixes:
        story.append(Paragraph("Critical Fixes", styles["SectionHeader"]))
        for f in fixes:
            story.append(Paragraph(f"&bull; {f}", styles["BulletItem"]))

    # ── Job Match (optional) ──
    if match and match.get("success"):
        story.append(HRFlowable(width="100%", color=colors.HexColor("#dddddd")))
        story.append(Paragraph("Job Match Results", styles["SectionHeader"]))

        percent = match.get("match_percent", 0)
        story.append(Paragraph(f"<b>Match:</b> {percent}%", styles["Body"]))
        story.append(Paragraph(match.get("match_summary", "—"), styles["Body"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Recommendation:</b> {match.get('recommendation','—')}", styles["Body"]))
        story.append(Spacer(1, 6))

        story.append(Paragraph(f"<b>Matched keywords:</b> {_skill_list(match.get('matched_keywords', []))}", styles["Body"]))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Missing keywords:</b> {_skill_list(match.get('missing_keywords', []), 'None flagged')}", styles["Body"]))

        rewrites = match.get("bullet_rewrites", [])
        if rewrites:
            story.append(Paragraph("Tailored Bullet Rewrites", styles["SectionHeader"]))
            for r in rewrites:
                story.append(Paragraph(f"<font color='#c0392b'>Original:</font> {r.get('original','')}", styles["Body"]))
                story.append(Paragraph(f"<font color='#1e8449'>Rewritten:</font> {r.get('rewritten','')}", styles["Body"]))
                story.append(Spacer(1, 6))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# ── Quick test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample_analysis = {
        "ats_score": 72,
        "overall_verdict": "Solid resume, needs stronger quantified bullets.",
        "score_breakdown": {"formatting": 16, "keywords": 18, "experience": 17, "skills": 14, "education": 7},
        "detected_skills": ["Python", "SQL", "Git"],
        "missing_skills": ["AWS", "Docker"],
        "weak_phrases": [{"original": "Helped with project", "suggestion": "Led cross-functional project delivering X"}],
        "section_feedback": {"summary": "Clear but generic.", "experience": "Good, needs metrics."},
        "top_strengths": ["Strong technical foundation"],
        "critical_fixes": ["Add measurable outcomes to bullets"]
    }
    pdf = generate_pdf_report(sample_analysis, resume_name="test_resume.pdf")
    with open("test_report.pdf", "wb") as f:
        f.write(pdf)
    print(f"PDF generated: {len(pdf)} bytes -> test_report.pdf")