"""
app.py — Main Streamlit app for Resume Analyzer
UI Redesign Part 1: Landing page + sidebar
"""

import os
import streamlit as st
from config import (
    APP_TITLE, APP_SUBTITLE, SIDEBAR_TITLE,
    ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB,
    UPLOAD_DIR, validate_config
)
from parser import parse_resume
from analyzer import analyze_resume, get_score_label
from job_matcher import match_job, get_match_label
from report_generator import generate_pdf_report

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-main:        #0b0d14;
    --bg-card:        #111420;
    --bg-card-hover:  #161a2b;
    --border:         #1e2235;
    --border-light:   #252a40;
    --accent:         #4f7cff;
    --accent-soft:    #7c5cfc;
    --accent-glow:    rgba(79,124,255,0.18);
    --success:        #22d3a5;
    --success-bg:     #0a1f1a;
    --warning:        #f4b942;
    --warning-bg:     #1f190a;
    --danger:         #f06464;
    --danger-bg:      #1f0a0a;
    --text-primary:   #eef0f8;
    --text-secondary: #7a82a0;
    --text-muted:     #4a5068;
    --radius-sm:      8px;
    --radius-md:      12px;
    --radius-lg:      18px;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-main);
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.main .block-container { padding-top: 1.5rem; max-width: 1100px; }

/* ════════════════════════════════
   SIDEBAR
════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1.2rem; }

.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.4rem;
}
.sidebar-logo-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, var(--accent), var(--accent-soft));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
}
.sidebar-logo-text {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}
.sidebar-logo-sub {
    font-size: 0.72rem;
    color: var(--text-secondary);
    font-weight: 400;
}

/* Upload zone */
[data-testid="stFileUploader"] {
    border: 1.5px dashed var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    padding: 1.1rem !important;
    background: var(--bg-main) !important;
    transition: border-color 0.2s, background 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
    background: var(--accent-glow) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: var(--text-secondary) !important;
    font-size: 0.88rem !important;
}

.upload-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.5rem;
}

.status-ok {
    background: var(--success-bg);
    border: 1px solid rgba(34,211,165,0.2);
    padding: 0.5rem 0.85rem;
    border-radius: var(--radius-sm);
    color: var(--success);
    font-size: 0.82rem;
    font-weight: 500;
    display: flex; align-items: center; gap: 6px;
}
.status-error {
    background: var(--danger-bg);
    border: 1px solid rgba(240,100,100,0.2);
    padding: 0.5rem 0.85rem;
    border-radius: var(--radius-sm);
    color: var(--danger);
    font-size: 0.82rem;
    font-weight: 500;
}
.status-ok, .status-error {
    display: inline-flex !important;
    width: fit-content;
}
.sidebar-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1rem 0;
}

.sidebar-info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-bottom: 0.4rem;
}
.sidebar-info-val {
    font-weight: 600;
    color: var(--text-primary);
}

.tip-box {
    background: var(--bg-main);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.75rem 0.9rem;
    font-size: 0.79rem;
    color: var(--text-secondary);
    line-height: 1.55;
    margin-top: 0.8rem;
}
.tip-box b { color: var(--text-primary); }

/* ════════════════════════════════
   LANDING PAGE
════════════════════════════════ */
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(79,124,255,0.1);
    border: 1px solid rgba(79,124,255,0.25);
    color: var(--accent);
    font-size: 0.78rem;
    font-weight: 600;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    margin-bottom: 1.2rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.15;
    letter-spacing: -0.03em;
    margin-bottom: 0.7rem;
}
.hero-title span {
    background: linear-gradient(90deg, var(--accent), var(--accent-soft));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    font-size: 1.05rem;
    color: var(--text-secondary);
    line-height: 1.65;
    max-width: 560px;
    margin-bottom: 2rem;
}

.hero-stats {
    display: flex;
    gap: 2rem;
    margin-bottom: 2.5rem;
}
.hero-stat-num {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
}
.hero-stat-label {
    font-size: 0.78rem;
    color: var(--text-secondary);
    margin-top: 0.2rem;
}

/* Feature cards */
.feat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 0.5rem;
}
.feat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.3rem;
    transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
    cursor: default;
}
.feat-card:hover {
    border-color: var(--accent);
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(79,124,255,0.1);
}
.feat-icon {
    width: 46px; height: 46px;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--accent), var(--accent-soft));
    display: flex; align-items: center; justify-content: center;
    font-size: 1.35rem;
    margin-bottom: 1rem;
}
.feat-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.4rem;
}
.feat-desc {
    font-size: 0.84rem;
    color: var(--text-secondary);
    line-height: 1.55;
}

/* How-it-works strip */
.how-strip {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 2rem;
    margin-top: 1.5rem;
}
.how-step {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    flex: 1;
    justify-content: center;
}
.how-num {
    width: 30px; height: 30px;
    background: linear-gradient(135deg, var(--accent), var(--accent-soft));
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
}
.how-text {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 500;
}
.how-text b { color: var(--text-primary); }
.how-arrow {
    color: var(--text-muted);
    font-size: 1.2rem;
    padding: 0 0.5rem;
    flex-shrink: 0;
}

/* ════════════════════════════════
   POST-UPLOAD (shared classes — Part 2/3 will build on these)
════════════════════════════════ */
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.4rem;
}
.page-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}
.page-sub {
    font-size: 0.88rem;
    color: var(--text-secondary);
    margin-top: 0.15rem;
}
.model-tag {
    background: rgba(79,124,255,0.1);
    border: 1px solid rgba(79,124,255,0.22);
    color: var(--accent);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.35rem 0.85rem;
    border-radius: 20px;
}

[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1.1rem;
    transition: border-color 0.2s;
}
[data-testid="stMetric"]:hover { border-color: var(--accent); }
[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; font-size: 0.8rem !important; }
[data-testid="stMetricValue"] { color: var(--text-primary) !important; font-weight: 700 !important; }

.section-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 0.3rem 0.75rem;
    border-radius: var(--radius-sm);
    font-size: 0.79rem;
    font-weight: 600;
    margin: 0.18rem;
}
.badge-found  { background: var(--success-bg); color: var(--success); border: 1px solid rgba(34,211,165,0.2); }
.badge-missing{ background: var(--danger-bg);  color: var(--danger);  border: 1px solid rgba(240,100,100,0.2); }

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 3px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 4px;
    width: fit-content;
}
[data-testid="stTabs"] button {
    font-weight: 600;
    font-size: 0.87rem;
    border-radius: var(--radius-sm) !important;
    color: var(--text-secondary) !important;
    padding: 0.45rem 1.1rem !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none; }

/* Buttons */
[data-testid="stDownloadButton"] button,
.stButton button[kind="primary"] {
    background: linear-gradient(90deg, var(--accent), var(--accent-soft)) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: var(--radius-sm) !important;
}

/* Preview box */
.preview-box {
    background: var(--bg-main);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.3rem;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 0.81rem;
    line-height: 1.7;
    color: var(--text-secondary);
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
}

/* Breakdown bars */
.breakdown-row { display: flex; align-items: center; margin-bottom: 0.65rem; }
.breakdown-label { width: 115px; font-size: 0.84rem; color: var(--text-secondary); font-weight: 500; }
.breakdown-bar-bg { flex: 1; background: var(--border); border-radius: 6px; height: 8px; overflow: hidden; margin: 0 0.7rem; }
.breakdown-bar-fill { height: 100%; border-radius: 6px; background: linear-gradient(90deg, var(--accent), var(--accent-soft)); }
.breakdown-score { width: 55px; font-size: 0.79rem; color: var(--text-muted); text-align: right; font-weight: 500; }

/* Chips */
.chip { display: inline-block; padding: 0.3rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.8rem; margin: 0.18rem; font-weight: 500; }
.chip-good    { background: var(--success-bg); color: var(--success); border: 1px solid rgba(34,211,165,0.2); }
.chip-missing { background: var(--warning-bg); color: var(--warning); border: 1px solid rgba(244,185,66,0.2); }

/* Weak phrase + rewrite cards */
.weak-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-left: 3px solid var(--warning); border-radius: var(--radius-sm);
    padding: 0.8rem 1rem; margin-bottom: 0.55rem; font-size: 0.86rem;
}
.weak-original  { color: var(--danger); text-decoration: line-through; opacity: 0.8; }
.weak-suggestion{ color: var(--success); }

.rewrite-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1rem 1.1rem; margin-bottom: 0.8rem; font-size: 0.85rem;
}
.rewrite-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.25rem; }
.rewrite-original-label { color: var(--danger); }
.rewrite-new-label      { color: var(--success); }
.rewrite-text { color: var(--text-secondary); margin-bottom: 0.7rem; }

/* Gauge (donut ring via conic-gradient) */
.gauge-wrap { width: 170px; height: 170px; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center; }
.gauge-inner {
    width: 130px; height: 130px; border-radius: 50%;
    background: var(--bg-card);
    border: 1px solid var(--border);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.gauge-num   { font-size: 2.2rem; font-weight: 800; line-height: 1; }
.gauge-lbl   { font-size: 0.72rem; color: var(--text-muted); margin-top: 0.3rem; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
/* ════════════════════════════════
   PART 2 — METRICS ROW
════════════════════════════════ */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.2rem;
}
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    transition: border-color 0.2s, transform 0.15s;
}
.metric-card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
}
.metric-card-accent {
    border-color: rgba(79,124,255,0.4);
    background: rgba(79,124,255,0.05);
}
.metric-icon {
    font-size: 1.3rem;
    flex-shrink: 0;
}
.metric-val {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.1;
}
.metric-lbl {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 0.15rem;
    font-weight: 500;
}

/* ════════════════════════════════
   PART 2 — SECTIONS PANEL
════════════════════════════════ */
.sections-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}
.sections-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.6rem;
}

/* ════════════════════════════════
   PART 2 — CTA PANELS (empty tab state)
════════════════════════════════ */
.cta-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 2rem 2rem 1.8rem;
    text-align: center;
    margin-bottom: 1.2rem;
}
.cta-icon {
    font-size: 2.2rem;
    margin-bottom: 0.6rem;
}
.cta-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.4rem;
}
.cta-sub {
    font-size: 0.87rem;
    color: var(--text-secondary);
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ════════════════════════════════
   PART 2 — TAB INTRO
════════════════════════════════ */
.tab-intro {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 0.8rem;
    padding: 0.6rem 0.9rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
}
[data-testid="stFileUploaderDropzone"] small {
    display: none !important;
}
            
/* ════════════════════════════════
   PART 3 — RESULT PANELS
════════════════════════════════ */
.result-top-panel {
    display: flex;
    align-items: center;
    gap: 2rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.8rem 2rem;
    margin-bottom: 1.2rem;
}
.result-gauge-col {
    flex-shrink: 0;
}
.result-verdict-col {
    flex: 1;
}
.verdict-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.4rem;
}
.verdict-text {
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.65;
    margin-bottom: 1rem;
}
.recommendation-box {
    background: rgba(79,124,255,0.07);
    border: 1px solid rgba(79,124,255,0.2);
    border-radius: var(--radius-sm);
    padding: 0.65rem 1rem;
    font-size: 0.85rem;
    color: var(--accent);
    font-weight: 500;
    line-height: 1.5;
}

.result-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.2rem 1.3rem;
    margin-bottom: 1rem;
}
.result-section-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.9rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
}
.result-section-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-top: -0.6rem;
    margin-bottom: 0.9rem;
}

.weak-arrow {
    color: var(--text-muted);
    font-weight: 600;
    margin: 0 0.3rem;
}

.strength-item {
    background: var(--success-bg);
    border: 1px solid rgba(34,211,165,0.15);
    border-radius: var(--radius-sm);
    padding: 0.55rem 0.9rem;
    font-size: 0.84rem;
    color: var(--success);
    margin-bottom: 0.45rem;
    line-height: 1.5;
}
.fix-item {
    background: var(--warning-bg);
    border: 1px solid rgba(244,185,66,0.15);
    border-radius: var(--radius-sm);
    padding: 0.55rem 0.9rem;
    font-size: 0.84rem;
    color: var(--warning);
    margin-bottom: 0.45rem;
    line-height: 1.5;
}
.empty-state {
    font-size: 0.83rem;
    color: var(--text-muted);
    font-style: italic;
}

</style>
""", unsafe_allow_html=True)

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS  (unchanged — keep your existing functions here)
# ══════════════════════════════════════════════════════════════════════════════

def save_uploaded_file(uploaded_file) -> str:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def is_valid_size(uploaded_file) -> bool:
    return (uploaded_file.size / (1024 * 1024)) <= MAX_FILE_SIZE_MB

def render_section_badges(sections: dict):
    html = ""
    labels = {
        "contact":"📞 Contact","summary":"📝 Summary","experience":"💼 Experience",
        "education":"🎓 Education","skills":"⚡ Skills","projects":"🚀 Projects",
        "certifications":"🏆 Certs","awards":"🥇 Awards",
    }
    for key, label in labels.items():
        cls = "badge-found" if sections.get(key, False) else "badge-missing"
        html += f'<span class="section-badge {cls}">{label}</span>'
    return html

def render_gauge(value: int, label: str, color: str, suffix: str = ""):
    pct = max(0, min(100, value))
    return f"""
    <div class="gauge-wrap" style="background: conic-gradient({color} {pct * 3.6}deg, var(--border) {pct * 3.6}deg);">
        <div class="gauge-inner">
            <div class="gauge-num" style="color:{color};">{value}{suffix}</div>
            <div class="gauge-lbl">{label}</div>
        </div>
    </div>"""

def render_breakdown_bar(label: str, score: int, max_score: int):
    pct = int((score / max_score) * 100) if max_score else 0
    return f"""
    <div class="breakdown-row">
        <div class="breakdown-label">{label}</div>
        <div class="breakdown-bar-bg"><div class="breakdown-bar-fill" style="width:{pct}%;"></div></div>
        <div class="breakdown-score">{score}/{max_score}</div>
    </div>"""

def render_analysis_results(analysis: dict):
    score = analysis.get("ats_score", 0)
    label, color = get_score_label(score)

    # ── TOP PANEL: gauge + verdict ──
    st.markdown(f"""
    <div class="result-top-panel">
        <div class="result-gauge-col">
            {render_gauge(score, label, color)}
        </div>
        <div class="result-verdict-col">
            <div class="verdict-label">Overall Verdict</div>
            <div class="verdict-text">{analysis.get("overall_verdict", "—")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SCORE BREAKDOWN ──
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    st.markdown('<div class="result-section-title">📊 Score Breakdown</div>', unsafe_allow_html=True)
    breakdown = analysis.get("score_breakdown", {})
    max_scores = {"formatting": 20, "keywords": 25, "experience": 25, "skills": 20, "education": 10}
    bars_html = "".join(render_breakdown_bar(k.capitalize(), breakdown.get(k, 0), v) for k, v in max_scores.items())
    st.markdown(bars_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── SKILLS ROW ──
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-title">✅ Skills Detected</div>', unsafe_allow_html=True)
        chips = "".join(f'<span class="chip chip-good">{s}</span>' for s in analysis.get("detected_skills", []))
        st.markdown(chips or '<span class="empty-state">None detected</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-title">⚠️ Missing Skills</div>', unsafe_allow_html=True)
        chips = "".join(f'<span class="chip chip-missing">{s}</span>' for s in analysis.get("missing_skills", []))
        st.markdown(chips or '<span class="empty-state">None flagged</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── WEAK LANGUAGE ──
    weak_phrases = analysis.get("weak_phrases", [])
    if weak_phrases:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-title">✍️ Weak Language → Suggested Fixes</div>', unsafe_allow_html=True)
        for wp in weak_phrases:
            st.markdown(f'''
            <div class="weak-card">
                <span class="weak-original">{wp.get("original","")}</span>
                <span class="weak-arrow"> → </span>
                <span class="weak-suggestion">{wp.get("suggestion","")}</span>
            </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── SECTION FEEDBACK ──
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    st.markdown('<div class="result-section-title">🗂️ Section-by-Section Feedback</div>', unsafe_allow_html=True)
    for section, feedback in analysis.get("section_feedback", {}).items():
        with st.expander(f"📌 {section.capitalize()}"):
            st.write(feedback)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── STRENGTHS + FIXES ──
    col_s, col_f = st.columns(2)
    with col_s:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-title">💪 Top Strengths</div>', unsafe_allow_html=True)
        for s in analysis.get("top_strengths", []):
            st.markdown(f'<div class="strength-item">✅ {s}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_f:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-title">🔧 Critical Fixes</div>', unsafe_allow_html=True)
        for f in analysis.get("critical_fixes", []):
            st.markdown(f'<div class="fix-item">⚠️ {f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def render_match_results(match: dict):
    percent = match.get("match_percent", 0)
    label, color = get_match_label(percent)

    # ── TOP PANEL: gauge + summary ──
    st.markdown(f"""
    <div class="result-top-panel">
        <div class="result-gauge-col">
            {render_gauge(percent, label, color, suffix="%")}
        </div>
        <div class="result-verdict-col">
            <div class="verdict-label">Match Summary</div>
            <div class="verdict-text">{match.get("match_summary", "—")}</div>
            <div class="recommendation-box">
                💡 {match.get("recommendation", "—")}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KEYWORDS ROW ──
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-title">✅ Matched Keywords</div>', unsafe_allow_html=True)
        chips = "".join(f'<span class="chip chip-good">{s}</span>' for s in match.get("matched_keywords", []))
        st.markdown(chips or '<span class="empty-state">None matched</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-title">⚠️ Missing Keywords</div>', unsafe_allow_html=True)
        chips = "".join(f'<span class="chip chip-missing">{s}</span>' for s in match.get("missing_keywords", []))
        st.markdown(chips or '<span class="empty-state">None flagged</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── BULLET REWRITES ──
    rewrites = match.get("bullet_rewrites", [])
    if rewrites:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('''
        <div class="result-section-title">✍️ Tailored Bullet Rewrites</div>
        <div class="result-section-sub">Rewritten to match this specific job posting</div>
        ''', unsafe_allow_html=True)
        for r in rewrites:
            st.markdown(f'''
            <div class="rewrite-card">
                <div class="rewrite-label rewrite-original-label">ORIGINAL</div>
                <div class="rewrite-text">{r.get("original","")}</div>
                <div class="rewrite-label rewrite-new-label">REWRITTEN FOR THIS ROLE</div>
                <div class="rewrite-text">{r.get("rewritten","")}</div>
            </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🎯</div>
        <div>
            <div class="sidebar-logo-text">ResumeAI</div>
            <div class="sidebar-logo-sub">Powered by Gemini 2.5</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    config_ok, config_msg = validate_config()
    if config_ok:
        st.markdown('<div class="status-ok">🟢 &nbsp;API Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-error">⚠️ {config_msg}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.markdown('<div class="upload-label">Upload Resume</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        label="", type=ALLOWED_EXTENSIONS,
        help=f"PDF or DOCX · Max {MAX_FILE_SIZE_MB}MB",
        label_visibility="collapsed"
    )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sidebar-info-row"><span>Formats</span><span class="sidebar-info-val">PDF · DOCX</span></div>
    <div class="sidebar-info-row"><span>Max size</span><span class="sidebar-info-val">{MAX_FILE_SIZE_MB} MB</span></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tip-box">
        💡 <b>Best results:</b> Upload a single-column resume without tables or text boxes — they confuse ATS parsers the same way they'd confuse real recruiters.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════

if uploaded_file is None:
    # ── LANDING PAGE ──
    st.markdown("""
<div class="hero-title">Land more interviews with a<br><span>smarter resume</span></div>
<div class="hero-sub">Upload your resume and get an ATS score, skill gap analysis, and tailored job match in seconds — powered by Gemini AI.</div>
""", unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-stats">
        <div><div class="hero-stat-num">98%</div><div class="hero-stat-label">ATS compatibility check</div></div>
        <div><div class="hero-stat-num">~10s</div><div class="hero-stat-label">Average analysis time</div></div>
        <div><div class="hero-stat-num">0–100</div><div class="hero-stat-label">Detailed score breakdown</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feat-grid">
        <div class="feat-card">
            <div class="feat-icon">📊</div>
            <div class="feat-title">ATS Score</div>
            <div class="feat-desc">Get a 0–100 score showing exactly how well your resume passes Applicant Tracking Systems — with a full breakdown.</div>
        </div>
        <div class="feat-card">
            <div class="feat-icon">🔍</div>
            <div class="feat-title">Skill Gap Analysis</div>
            <div class="feat-desc">See detected skills, missing keywords, and weak language — with AI-suggested fixes for every issue.</div>
        </div>
        <div class="feat-card">
            <div class="feat-icon">💼</div>
            <div class="feat-title">Job Matching</div>
            <div class="feat-desc">Paste any job description and get a match % with tailored bullet point rewrites specific to that role.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="how-strip">
        <div class="how-step">
            <div class="how-num">1</div>
            <div class="how-text"><b>Upload</b> your PDF or DOCX</div>
        </div>
        <div class="how-arrow">→</div>
        <div class="how-step">
            <div class="how-num">2</div>
            <div class="how-text"><b>Analyze</b> with one click</div>
        </div>
        <div class="how-arrow">→</div>
        <div class="how-step">
            <div class="how-num">3</div>
            <div class="how-text"><b>Fix</b> issues & match jobs</div>
        </div>
        <div class="how-arrow">→</div>
        <div class="how-step">
            <div class="how-num">4</div>
            <div class="how-text"><b>Download</b> your PDF report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # ── POST-UPLOAD DASHBOARD ──
    if not is_valid_size(uploaded_file):
        st.error(f"❌ File exceeds {MAX_FILE_SIZE_MB}MB limit.")
        st.stop()

    file_path = save_uploaded_file(uploaded_file)
    with st.spinner("📖 Reading your resume..."):
        result = parse_resume(file_path)

    if not result["success"]:
        st.error(f"❌ Could not read file: {result['error']}")
        st.stop()

    st.session_state["resume_text"] = result["text"]
    st.session_state["resume_parsed"] = True

    analysis_key = f"analysis_{uploaded_file.name}_{uploaded_file.size}"
    match_key    = f"match_{uploaded_file.name}_{uploaded_file.size}"

    # ── DASHBOARD HEADER ──
    fname = uploaded_file.name
    has_analysis = analysis_key in st.session_state and st.session_state[analysis_key].get("success")

    st.markdown(f"""
    <div class="page-header">
        <div>
            <div class="page-title">Resume Dashboard</div>
            <div class="page-sub">📄 {fname}</div>
        </div>
        <div class="model-tag">⚡ Gemini 2.5 Flash</div>
    </div>
    """, unsafe_allow_html=True)

    # ── METRICS ROW ──
    file_size_kb = uploaded_file.size / 1024
    word_count   = result["word_count"]
    page_count   = result["page_count"]
    found_count  = sum(result["sections"].values())
    total_sects  = len(result["sections"])

    ats_score_display = "—"
    match_pct_display = "—"
    if has_analysis:
        ats_score_display = f"{st.session_state[analysis_key].get('ats_score', 0)}/100"
    if match_key in st.session_state and st.session_state[match_key].get("success"):
        match_pct_display = f"{st.session_state[match_key].get('match_percent', 0)}%"

    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-card">
            <div class="metric-icon">📝</div>
            <div class="metric-body">
                <div class="metric-val">{word_count:,}</div>
                <div class="metric-lbl">Word Count</div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">📑</div>
            <div class="metric-body">
                <div class="metric-val">{page_count}</div>
                <div class="metric-lbl">Pages</div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">📦</div>
            <div class="metric-body">
                <div class="metric-val">{file_size_kb:.0f} KB</div>
                <div class="metric-lbl">File Size</div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">🗂️</div>
            <div class="metric-body">
                <div class="metric-val">{found_count}/{total_sects}</div>
                <div class="metric-lbl">Sections Found</div>
            </div>
        </div>
        <div class="metric-card {'metric-card-accent' if has_analysis else ''}">
            <div class="metric-icon">🎯</div>
            <div class="metric-body">
                <div class="metric-val">{ats_score_display}</div>
                <div class="metric-lbl">ATS Score</div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">💼</div>
            <div class="metric-body">
                <div class="metric-val">{match_pct_display}</div>
                <div class="metric-lbl">Job Match</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTIONS DETECTED ──
    st.markdown("""
    <div class="sections-panel">
        <div class="sections-title">Sections Detected</div>
    """, unsafe_allow_html=True)
    st.markdown(render_section_badges(result["sections"]), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── DOWNLOAD (if analysis exists) ──
    if has_analysis:
        pdf_bytes = generate_pdf_report(
            analysis=st.session_state[analysis_key],
            match=st.session_state.get(match_key),
            resume_name=uploaded_file.name
        )
        st.markdown("<div style='margin: 0.8rem 0 0.2rem'>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Download Full Report (PDF)",
            data=pdf_bytes,
            file_name=f"resume_analysis_{fname.rsplit('.', 1)[0]}.pdf",
            mime="application/pdf",
            type="primary"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.2rem'>", unsafe_allow_html=True)

    # ── TABS ──
    tab1, tab2, tab3 = st.tabs(["📋 Resume Preview", "🎯 ATS Analysis", "💼 Job Match"])

    with tab1:
        st.markdown("""
        <div class="tab-intro">
            Exactly what the AI reads — verify your content parsed correctly before analyzing.
        </div>
        """, unsafe_allow_html=True)
        preview_text = result["text"][:3000]
        if len(result["text"]) > 3000:
            preview_text += f"\n\n... [{len(result['text']) - 3000} more characters]"
        st.markdown(f'<div class="preview-box">{preview_text}</div>', unsafe_allow_html=True)

    with tab2:
        if not (analysis_key in st.session_state and st.session_state[analysis_key].get("success")):
            st.markdown("""
            <div class="cta-panel">
                <div class="cta-icon">🎯</div>
                <div class="cta-title">Ready to analyze your resume?</div>
                <div class="cta-sub">Get an ATS score, skill gap report, weak language fixes, and section-by-section feedback in ~10 seconds.</div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("🚀 Analyze My Resume", type="primary"):
            with st.spinner("🤖 Analyzing with AI..."):
                analysis = analyze_resume(st.session_state["resume_text"])
            st.session_state[analysis_key] = analysis
            st.rerun()
        if analysis_key in st.session_state:
            analysis = st.session_state[analysis_key]
            if analysis["success"]:
                render_analysis_results(analysis)
            else:
                st.error(f"❌ {analysis['error']}")

    with tab3:
        if not (match_key in st.session_state and st.session_state[match_key].get("success")):
            st.markdown("""
            <div class="cta-panel">
                <div class="cta-icon">💼</div>
                <div class="cta-title">Match your resume to a job</div>
                <div class="cta-sub">Paste any job posting below — get a match %, keyword gaps, and tailored bullet point rewrites for that exact role.</div>
            </div>
            """, unsafe_allow_html=True)
        job_description = st.text_area(
            "", placeholder="Paste the full job description here...",
            height=200, key="job_description_input"
        )
        col_btn, col_hint = st.columns([1, 3])
        with col_btn:
            run_match = st.button("🔍 Analyze Match", type="primary")
        with col_hint:
            if not job_description or len(job_description.strip()) < 50:
                st.caption("⏳ Paste at least 50 characters to enable matching")
        if run_match:
            if not job_description or len(job_description.strip()) < 50:
                st.error("❌ Paste a fuller job description first (50+ characters).")
            else:
                with st.spinner("🤖 Comparing resume against job posting..."):
                    match = match_job(st.session_state["resume_text"], job_description)
                st.session_state[match_key] = match
                st.rerun()
        if match_key in st.session_state:
            match = st.session_state[match_key]
            if match["success"]:
                render_match_results(match)
            else:
                st.error(f"❌ {match['error']}")

    st.markdown("</div>", unsafe_allow_html=True)