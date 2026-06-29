"""
job_matcher.py — Match resume against a specific job description
Phase 4: Match %, missing keywords, tailored bullet rewrites
"""

import json
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL


# ══════════════════════════════════════════════════════════════════════════════
#  CLIENT SETUP
# ══════════════════════════════════════════════════════════════════════════════

def get_client():
    return genai.Client(api_key=GEMINI_API_KEY)


# ══════════════════════════════════════════════════════════════════════════════
#  THE MASTER PROMPT
# ══════════════════════════════════════════════════════════════════════════════

MATCH_PROMPT = """You are an expert recruiter and resume coach comparing a candidate's resume against a specific job description.

Analyze how well the resume matches the job description below and return a JSON object with EXACTLY this structure — no extra text, no markdown, no explanation, just raw JSON:

{{
  "match_percent": <integer 0-100>,
  "match_summary": "<2-3 sentence summary of overall fit>",
  "matched_keywords": [<list of important keywords/skills from the JD that ARE present in the resume>],
  "missing_keywords": [<list of important keywords/skills from the JD that are NOT present in the resume>],
  "bullet_rewrites": [
    {{
      "original": "<an existing resume bullet point>",
      "rewritten": "<the same bullet rewritten to better match this specific job, using relevant keywords and stronger language>"
    }}
  ],
  "recommendation": "<1-2 sentence actionable recommendation for improving fit for this specific role>"
}}

Guidelines:
- match_percent should reflect realistic alignment: skills overlap, experience relevance, and seniority fit
- matched_keywords and missing_keywords should be specific technical/soft skills or requirements mentioned in the JD, not generic words
- bullet_rewrites should pick 3-4 of the most relevant existing resume bullets and rewrite them to better target this job, weaving in JD keywords naturally without fabricating experience the candidate doesn't have
- Be honest — do not inflate the match percentage to be encouraging

RESUME:
---
{resume_text}
---

JOB DESCRIPTION:
---
{job_description}
---

Return ONLY the JSON. No preamble, no explanation."""


# ══════════════════════════════════════════════════════════════════════════════
#  CORE MATCHING FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def match_job(resume_text: str, job_description: str) -> dict:
    """
    Compare resume against a job description using Gemini.
    Returns dict with match data + success/error fields.
    """
    result = {
        "success": False,
        "error": None,
        "match_percent": 0,
        "match_summary": "",
        "matched_keywords": [],
        "missing_keywords": [],
        "bullet_rewrites": [],
        "recommendation": ""
    }

    if not resume_text or len(resume_text.strip()) < 50:
        result["error"] = "Resume text too short to analyze."
        return result

    if not job_description or len(job_description.strip()) < 50:
        result["error"] = "Job description too short — please paste the full posting."
        return result

    try:
        client = get_client()

        trimmed_resume = resume_text[:4000]
        trimmed_jd = job_description[:3000]

        prompt = MATCH_PROMPT.format(
            resume_text=trimmed_resume,
            job_description=trimmed_jd
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        raw = response.text.strip()

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
            result["error"] = f"Matching failed: {error_msg}"

    return result


# ══════════════════════════════════════════════════════════════════════════════
#  MATCH LABEL HELPER
# ══════════════════════════════════════════════════════════════════════════════

def get_match_label(percent: int) -> tuple:
    """Returns (label, color) based on match percentage."""
    if percent >= 80:
        return "Strong Match", "#00e676"
    elif percent >= 60:
        return "Good Match", "#ffeb3b"
    elif percent >= 40:
        return "Partial Match", "#ff9800"
    else:
        return "Weak Match", "#ff1744"


# ── Quick test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample_resume = """
    Software Engineer with 3 years experience in React and JavaScript.
    Built and maintained dashboard features, fixed bugs, worked on payment integrations.
    Skills: JavaScript, React, HTML, CSS, Git, REST APIs.
    """

    sample_jd = """
    We are looking for a Senior Frontend Engineer with strong React and TypeScript
    experience. Must have experience with state management (Redux), testing
    (Jest, React Testing Library), and CI/CD pipelines. Cloud experience (AWS) a plus.
    """

    print("Testing job matcher...")
    r = match_job(sample_resume, sample_jd)
    if r["success"]:
        print(f"Match: {r['match_percent']}%")
        print(f"Missing: {r['missing_keywords']}")
    else:
        print(f"Error: {r['error']}")