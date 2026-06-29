"""
analyzer.py — AI-powered resume analysis using Gemini
Phase 3: ATS scoring, skill detection, and section feedback
"""

import json
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_TOKENS


# ══════════════════════════════════════════════════════════════════════════════
#  CLIENT SETUP
# ══════════════════════════════════════════════════════════════════════════════

def get_client():
    return genai.Client(api_key=GEMINI_API_KEY)


# ══════════════════════════════════════════════════════════════════════════════
#  THE MASTER PROMPT
# ══════════════════════════════════════════════════════════════════════════════

ANALYSIS_PROMPT = """You are an expert ATS (Applicant Tracking System) resume analyzer and career coach.

Analyze the resume below and return a JSON object with EXACTLY this structure — no extra text, no markdown, no explanation, just raw JSON:

{{
  "ats_score": <integer 0-100>,
  "score_breakdown": {{
    "formatting": <integer 0-20>,
    "keywords": <integer 0-25>,
    "experience": <integer 0-25>,
    "skills": <integer 0-20>,
    "education": <integer 0-10>
  }},
  "detected_skills": [<list of skills found in resume>],
  "missing_skills": [<list of important skills NOT found but common for this type of role>],
  "weak_phrases": [
    {{"original": "<weak phrase>", "suggestion": "<stronger version>"}}
  ],
  "section_feedback": {{
    "summary": "<feedback or 'Section not found'>",
    "experience": "<feedback or 'Section not found'>",
    "education": "<feedback or 'Section not found'>",
    "skills": "<feedback or 'Section not found'>",
    "projects": "<feedback or 'Section not found'>"
  }},
  "top_strengths": [<3 specific strengths of this resume>],
  "critical_fixes": [<3 most important things to fix immediately>],
  "overall_verdict": "<2-3 sentence summary verdict>"
}}

Scoring guide:
- formatting (0-20): Clean layout, consistent fonts, proper sections, no tables/columns that break ATS
- keywords (0-25): Industry-relevant keywords, action verbs, measurable results
- experience (0-25): Clear job titles, dates, company names, quantified achievements
- skills (0-20): Technical and soft skills section present and relevant
- education (0-10): Degree, institution, graduation year clearly stated

RESUME TO ANALYZE:
---
{resume_text}
---

Return ONLY the JSON. No preamble, no explanation."""


# ══════════════════════════════════════════════════════════════════════════════
#  CORE ANALYSIS FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def analyze_resume(resume_text: str) -> dict:
    """
    Send resume to Gemini and get structured analysis back.
    Returns dict with analysis data + success/error fields.
    """
    result = {
        "success": False,
        "error": None,
        "ats_score": 0,
        "score_breakdown": {},
        "detected_skills": [],
        "missing_skills": [],
        "weak_phrases": [],
        "section_feedback": {},
        "top_strengths": [],
        "critical_fixes": [],
        "overall_verdict": ""
    }

    if not resume_text or len(resume_text.strip()) < 50:
        result["error"] = "Resume text too short to analyze."
        return result

    try:
        client = get_client()

        # Trim to avoid token limits
        trimmed_text = resume_text[:4000]
        prompt = ANALYSIS_PROMPT.format(resume_text=trimmed_text)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        raw = response.text.strip()

        # Strip markdown fences if Gemini wraps in ```json
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        parsed = json.loads(raw)

        result.update(parsed)
        result["success"] = True

    except json.JSONDecodeError as e:
        result["error"] = f"AI returned invalid JSON: {str(e)}"
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg or "credentials" in error_msg.lower() or "API key not valid" in error_msg:
            result["error"] = "Invalid API key. Check your .env file."
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
            result["error"] = "Rate limit hit. Wait a moment and try again."
        else:
            result["error"] = f"Analysis failed: {error_msg}"

    return result


# ══════════════════════════════════════════════════════════════════════════════
#  SCORE LABEL HELPER
# ══════════════════════════════════════════════════════════════════════════════

def get_score_label(score: int) -> tuple:
    """Returns (label, color) based on ATS score."""
    if score >= 80:
        return "Excellent", "#00e676"
    elif score >= 60:
        return "Good", "#ffeb3b"
    elif score >= 40:
        return "Needs Work", "#ff9800"
    else:
        return "Poor", "#ff1744"


# ── Quick test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = """
    John Doe | john@email.com | LinkedIn: linkedin.com/in/johndoe

    SUMMARY
    Software engineer with 3 years experience in Python and web development.

    EXPERIENCE
    Software Engineer — TechCorp (2021–2024)
    - Worked on backend APIs
    - Did database stuff
    - Helped team with projects

    EDUCATION
    BS Computer Science — State University (2021)

    SKILLS
    Python, JavaScript, SQL, Git
    """

    print("Testing analyzer...")
    r = analyze_resume(sample)
    if r["success"]:
        print(f"ATS Score : {r['ats_score']}/100")
        print(f"Strengths : {r['top_strengths']}")
        print(f"Fix these : {r['critical_fixes']}")
    else:
        print(f"Error: {r['error']}")