"""AI RESUME ANALYZER & JOB RECOMMENDATION SYSTEM
Major College Project - Data Science & AI/ML
Run locally: streamlit run app.py
"""
import io
import json
import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

# Ensure script directory is prioritized in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv()

# Safe imports from local modules with robust fallbacks
try:
    from resume_parser import extract_text, get_resume_metadata, ResumeError, MAX_MB
except ImportError:
    from resume_parser import extract_text, ResumeError, MAX_MB

    def get_resume_metadata(filename: str, data: bytes = b"", text: str = "") -> dict:
        words = text.split() if text else []
        word_count = len(words)
        char_count = len(text) if text else 0
        reading_time_min = max(1, round(word_count / 200)) if word_count else 0
        size_kb = round(len(data) / 1024, 1) if data else 0.0
        ext = os.path.splitext(filename)[1].upper().replace(".", "") if filename else "UNKNOWN"
        return {
            "filename": filename or "Unknown",
            "extension": ext,
            "size_kb": size_kb,
            "word_count": word_count,
            "char_count": char_count,
            "reading_time_min": reading_time_min,
        }

from text_cleaner import clean_text, redact_personal_info
from skill_extractor import load_skill_dictionary, extract_skills, flatten
from job_matcher import load_roles, rank_roles, skill_gap, W_COVERAGE, W_TFIDF
from roadmap_generator import build_roadmap, build_report, build_markdown_report, build_json_report

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer & Job Recommendation System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# CUSTOM CSS FOR AI SAAS STYLING (Blue, Purple & Clean White Palette)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* SaaS Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #6d28d9 100%);
        border-radius: 16px;
        padding: 32px 36px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(55, 48, 163, 0.25);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 10px 0;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #e0e7ff;
        margin-bottom: 12px;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: #ffffff;
    }
    
    /* Metric & Feature Cards */
    .feature-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .feature-icon {
        font-size: 1.8rem;
        margin-bottom: 12px;
    }
    .feature-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }
    .feature-desc {
        font-size: 0.92rem;
        color: #64748b;
        line-height: 1.5;
    }
    
    /* Skill Pills */
    .skill-pill {
        display: inline-block;
        background: #ede9fe;
        color: #5b21b6;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px 3px;
        border: 1px solid #ddd6fe;
    }
    .skill-pill-matched {
        display: inline-block;
        background: #dcfce7;
        color: #15803d;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px 3px;
        border: 1px solid #bbf7d0;
    }
    .skill-pill-missing {
        display: inline-block;
        background: #fee2e2;
        color: #b91c1c;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px 3px;
        border: 1px solid #fecaca;
    }
    
    /* Recommendation Podium Cards */
    .podium-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
        text-align: center;
        margin-bottom: 16px;
    }
    .podium-rank {
        font-size: 1.6rem;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .podium-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }
    .podium-score {
        font-size: 2rem;
        font-weight: 800;
        color: #4338ca;
        margin-bottom: 10px;
    }
    
    /* Academic Disclaimer Banner */
    .disclaimer-box {
        background: #f8fafc;
        border-left: 4px solid #4338ca;
        padding: 14px 18px;
        border-radius: 8px;
        font-size: 0.88rem;
        color: #475569;
        margin-top: 24px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# DATA LOADING WITH CACHING
# -----------------------------------------------------------------------------
@st.cache_data
def load_application_datasets():
    """Load skill dictionary and job roles with path fallback."""
    dict_path = os.path.join(BASE_DIR, "data", "skill_dictionary.csv")
    roles_path = os.path.join(BASE_DIR, "data", "job_roles.csv")
    return load_skill_dictionary(dict_path), load_roles(roles_path)


skills_df, roles_df = load_application_datasets()


# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
def init_session_state():
    defaults = {
        "uploaded_filename": None,
        "raw_text": None,
        "clean_text": None,
        "found_by_cat": {},
        "found_skills": [],
        "metadata": {},
        "target_role": roles_df["role"].iloc[0] if not roles_df.empty else "Data Analyst",
        "ranking_df": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session_state()


def process_resume_data(filename: str, file_bytes: bytes):
    """Process uploaded or sample resume bytes in-memory and update session state."""
    try:
        raw_text = extract_text(filename, file_bytes)
    except ResumeError as err:
        st.error(f"❌ {err}")
        return False
    
    cleaned = clean_text(raw_text)
    found_by_cat = extract_skills(cleaned, skills_df)
    found_skills = flatten(found_by_cat)
    metadata = get_resume_metadata(filename, file_bytes, raw_text)
    ranking = rank_roles(cleaned, found_skills, roles_df)

    st.session_state["uploaded_filename"] = filename
    st.session_state["raw_text"] = raw_text
    st.session_state["clean_text"] = cleaned
    st.session_state["found_by_cat"] = found_by_cat
    st.session_state["found_skills"] = found_skills
    st.session_state["metadata"] = metadata
    st.session_state["ranking_df"] = ranking
    return True


# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎓 Academic Major Project")
    st.markdown("## 📄 Resume Analyzer AI")
    st.caption("AI/NLP Career Guidance & Job Matching Engine")
    st.markdown("---")

    page = st.radio(
        "Navigation Menu",
        [
            "🏠 Home Dashboard",
            "📤 Resume Upload",
            "🧩 Resume Analysis",
            "🎯 Job Recommendation",
            "🔍 Skill Gap Analysis",
            "🗺️ Learning Roadmap",
            "📄 Download Report",
        ],
        index=0,
    )

    st.markdown("---")
    st.markdown("#### 🎯 Select Target Role")
    all_roles = roles_df["role"].tolist()
    target_idx = all_roles.index(st.session_state["target_role"]) if st.session_state["target_role"] in all_roles else 0
    selected_target = st.selectbox("Role to evaluate against:", all_roles, index=target_idx)
    st.session_state["target_role"] = selected_target

    st.markdown("---")
    st.markdown("#### ⚡ Quick Sample Resumes")
    sample_options = {
        "Data Analyst (PDF)": "resume_A_data_analyst.pdf",
        "ML Engineer (DOCX)": "resume_B_ml_engineer.docx",
        "NLP Engineer (PDF)": "resume_C_nlp_engineer.pdf",
        "Software Engineer (DOCX)": "resume_D_fullstack_engineer.docx",
    }
    selected_sample = st.selectbox("Load sample for viva testing:", list(sample_options.keys()))
    if st.button("📥 Load Selected Sample", use_container_width=True):
        sample_filename = sample_options[selected_sample]
        sample_path = os.path.join(BASE_DIR, "sample_resumes", sample_filename)
        if not os.path.exists(sample_path):
            sample_path = os.path.join(BASE_DIR, "ai_resume_analyzer", "sample_resumes", sample_filename)
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                content = f.read()
            if process_resume_data(sample_filename, content):
                st.success(f"Loaded: {sample_filename}")
                st.rerun()

    st.markdown("---")
    st.caption(
        "🔒 **Privacy Protected:** Files are parsed strictly in memory and are never persisted to disk. "
        "Contact information is automatically redacted before NLP scoring."
    )


# -----------------------------------------------------------------------------
# PAGE 1: HOME DASHBOARD
# -----------------------------------------------------------------------------
if page == "🏠 Home Dashboard":
    st.markdown(
        """
        <div class="hero-banner">
            <span class="hero-badge">Major College Project • AI & Data Science</span>
            <h1 class="hero-title">AI Resume Analyzer & Job Recommendation System</h1>
            <p class="hero-subtitle">
                An intelligent Natural Language Processing (NLP) system designed to help engineering students
                benchmark their resumes against real-world tech industry roles, identify skill gaps, and follow
                curated weekly learning roadmaps.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("🚀 Start by Uploading Resume", use_container_width=True, type="primary"):
            st.session_state["nav_target"] = "📤 Resume Upload"
            st.info("Please click '📤 Resume Upload' in the sidebar to proceed with upload.")
    with col_btn2:
        if st.button("⚡ Test Alex Taylor - Data Analyst Resume", use_container_width=True):
            sample_path = os.path.join(BASE_DIR, "sample_resumes", "resume_A_data_analyst.pdf")
            if os.path.exists(sample_path):
                with open(sample_path, "rb") as f:
                    process_resume_data("resume_A_data_analyst.pdf", f.read())
                st.success("Loaded Alex Taylor sample resume! Head over to '🧩 Resume Analysis' or '🎯 Job Recommendation'.")

    st.markdown("### 🔄 How the System Works")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📤</div>
                <div class="feature-title">1. In-Memory Ingestion</div>
                <div class="feature-desc">
                    Accepts PDF and DOCX files up to 5 MB. Extracts text securely in memory without writing files to disk.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🛡️</div>
                <div class="feature-title">2. Responsible AI PII Scrub</div>
                <div class="feature-desc">
                    Redacts phone numbers, emails, and URLs. Normalizes text while preserving domain tokens like C++, C#, .NET, CI/CD.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">3. Hybrid Match Engine</div>
                <div class="feature-desc">
                    Computes 70% Skill Dictionary Coverage combined with 30% TF-IDF Cosine Similarity against industry job profiles.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🗺️</div>
                <div class="feature-title">4. Actionable Roadmap</div>
                <div class="feature-desc">
                    Identifies missing required skills and generates a structured week-by-week learning plan with hands-on projects.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🌟 Key Technical Highlights")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🎯 Objective Matching Formula")
        st.markdown(
            """
            - **70% Skill Coverage:** Percentage of required job skills explicitly found in the resume.
            - **30% TF-IDF Cosine Similarity:** Semantic vector similarity capturing technical context and role descriptions.
            - **Transparent Scoring:** No black-box claims; fully explainable heuristic model.
            """
        )
    with c2:
        st.markdown("#### 🔒 Privacy & Bias Mitigation")
        st.markdown(
            """
            - **Zero Disk Persistence:** Uploads vanish when session closes.
            - **Protected Attributes Excluded:** Gender, age, photo, nationality, and marital status are strictly unscored.
            - **Contact Redaction:** Personal contact details are filtered prior to NLP analysis.
            """
        )
    with c3:
        st.markdown("#### 📊 Comprehensive Deliverables")
        st.markdown(
            """
            - **Top 3 Role Recommendations** with clear rationale.
            - **Role-wise Comparison Charts** using interactive Plotly visuals.
            - **Instant Report Downloads** in Plain Text (.txt), Markdown (.md), and JSON (.json).
            """
        )

    st.markdown(
        """
        <div class="disclaimer-box">
            <strong>🎓 Academic Disclaimer:</strong> This system is developed as a student major project for guidance and skill discovery.
            Match scores are heuristic estimates to help candidates prepare for interviews and should not be used as an automated hiring or rejection gate.
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# PAGE 2: RESUME UPLOAD
# -----------------------------------------------------------------------------
elif page == "📤 Resume Upload":
    st.markdown("## 📤 Resume Ingestion & Validation")
    st.markdown("Upload your resume in PDF or DOCX format to initiate NLP text parsing and skill discovery.")

    uploaded_file = st.file_uploader(
        f"Choose a resume file (Supported formats: PDF, DOCX | Maximum size: {MAX_MB:g} MB)",
        type=["pdf", "docx"],
        help="Upload a standard PDF or DOCX file. Image-only scanned PDFs require OCR and are not supported.",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        with st.spinner("Parsing resume text and validating format..."):
            success = process_resume_data(uploaded_file.name, file_bytes)
        if success:
            st.success(f"✅ Successfully processed **{uploaded_file.name}** in memory!")

    if st.session_state["uploaded_filename"]:
        st.markdown("---")
        st.markdown("### 📋 Document Overview")
        meta = st.session_state["metadata"]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Uploaded File", meta.get("filename", "N/A"))
        col2.metric("Format", meta.get("extension", "N/A"))
        col3.metric("File Size", f"{meta.get('size_kb', 0):.1f} KB")
        col4.metric("Word Count", meta.get("word_count", 0))

        st.markdown("### 🔍 Text Extraction & Responsible AI Inspection")
        tab_raw, tab_redacted, tab_clean = st.tabs(["📄 Raw Extracted Text", "🛡️ PII-Redacted Text", "🧹 Normalized Text"])

        with tab_raw:
            st.text_area(
                "Raw text extracted from document:",
                st.session_state["raw_text"],
                height=240,
                disabled=True,
            )
        with tab_redacted:
            st.info("Notice that phone numbers, email addresses, and personal web URLs have been replaced with spaces.")
            st.text_area(
                "Text after PII scrubbing:",
                redact_personal_info(st.session_state["raw_text"]),
                height=240,
                disabled=True,
            )
        with tab_clean:
            st.caption("Cleaned, lowercased, and standardized while preserving domain tokens like C++, C#, .NET, and CI/CD.")
            st.text_area(
                "Cleaned text fed to NLP algorithms:",
                st.session_state["clean_text"],
                height=240,
                disabled=True,
            )
    else:
        st.info("👈 Please upload a PDF or DOCX file above, or select a sample resume from the sidebar to begin.")


# -----------------------------------------------------------------------------
# PAGE 3: RESUME ANALYSIS
# -----------------------------------------------------------------------------
elif page == "🧩 Resume Analysis":
    st.markdown("## 🧩 Resume Skill & Category Analysis")
    st.markdown("Detailed breakdown of technical competencies, tools, and platforms detected in your resume.")

    if not st.session_state["uploaded_filename"]:
        st.warning("⚠️ No resume loaded yet. Please upload a resume or select a sample resume from the sidebar.")
        st.stop()

    found_skills = st.session_state["found_skills"]
    found_by_cat = st.session_state["found_by_cat"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Skills Detected", len(found_skills))
    c2.metric("Skill Categories", len(found_by_cat))
    c3.metric("Vocabulary Coverage", f"{len(found_skills)} / {len(skills_df)} skills")
    quality_status = "High" if len(found_skills) >= 10 else ("Moderate" if len(found_skills) >= 5 else "Low")
    c4.metric("Profile Density", quality_status)

    if len(found_skills) < 5:
        st.warning(
            "⚠️ Fewer than 5 skills were detected. Ensure your resume contains recognizable technical keywords "
            "and that it is not an image-only scanned document."
        )

    st.markdown("---")
    col_chart, col_skills = st.columns([1, 1])

    with col_chart:
        st.markdown("### 📊 Skills by Category")
        cat_counts = {cat: len(skills) for cat, skills in sorted(found_by_cat.items())}
        if cat_counts:
            df_cat = pd.DataFrame(list(cat_counts.items()), columns=["Category", "Skill Count"])
            fig = px.pie(
                df_cat,
                values="Skill Count",
                names="Category",
                hole=0.45,
                color_discrete_sequence=px.colors.sequential.Indigo,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No categorized skills detected.")

    with col_skills:
        st.markdown("### 🏷️ Detected Skills List")
        if found_by_cat:
            for cat, items in sorted(found_by_cat.items()):
                st.markdown(f"**{cat}** ({len(items)})")
                pills_html = "".join([f'<span class="skill-pill">{s}</span>' for s in items])
                st.markdown(pills_html, unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
        else:
            st.write("No technical skills were identified.")


# -----------------------------------------------------------------------------
# PAGE 4: JOB RECOMMENDATION
# -----------------------------------------------------------------------------
elif page == "🎯 Job Recommendation":
    st.markdown("## 🎯 Job Role Recommendations & Match Benchmarks")
    st.markdown("Evaluation of your resume against all supported industry job roles using hybrid NLP scoring.")

    if not st.session_state["uploaded_filename"]:
        st.warning("⚠️ No resume loaded yet. Please upload a resume or select a sample resume from the sidebar.")
        st.stop()

    ranking = st.session_state["ranking_df"]
    target_role = st.session_state["target_role"]
    top3 = ranking.head(3)

    st.markdown("### 🏆 Top 3 Recommended Roles for Your Profile")
    pod_cols = st.columns(3)
    medals = ["🥇 1st Place", "🥈 2nd Place", "🥉 3rd Place"]

    for i, col in enumerate(pod_cols):
        r_item = top3.iloc[i]
        with col:
            st.markdown(
                f"""
                <div class="podium-card">
                    <div class="podium-rank">{medals[i]}</div>
                    <div class="podium-title">{r_item['role']}</div>
                    <div class="podium-score">{r_item['score']:.1f}%</div>
                    <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 8px;">
                        Skill Coverage: <strong>{r_item['coverage']:.0f}%</strong> • Semantic: <strong>{r_item['tfidf_cosine'] * 100:.1f}%</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("### 📊 Role-Wise Match Score Comparison")
    chart_df = ranking.sort_values("score", ascending=True)
    fig_bar = px.bar(
        chart_df,
        x="score",
        y="role",
        orientation="h",
        text="score",
        labels={"score": "Overall Match Score (%)", "role": "Job Role"},
        color="score",
        color_continuous_scale="Viridis",
        range_x=[0, 100],
    )
    fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=420)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("### 📋 Complete Benchmark Evaluation Matrix")
    display_df = ranking[["role", "score", "coverage", "tfidf_cosine", "explanation"]].copy()
    display_df.columns = ["Job Role", "Overall Score (%)", "Skill Coverage (%)", "TF-IDF Cosine", "Explanation & Rationale"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# -----------------------------------------------------------------------------
# PAGE 5: SKILL GAP ANALYSIS
# -----------------------------------------------------------------------------
elif page == "🔍 Skill Gap Analysis":
    st.markdown("## 🔍 Skill Gap Analysis")
    st.markdown(f"Comparative gap evaluation between your resume and the **{st.session_state['target_role']}** role.")

    if not st.session_state["uploaded_filename"]:
        st.warning("⚠️ No resume loaded yet. Please upload a resume or select a sample resume from the sidebar.")
        st.stop()

    target_role = st.session_state["target_role"]
    target_row = roles_df[roles_df["role"] == target_role].iloc[0]
    required_skills = target_row["skills"]
    found_skills = st.session_state["found_skills"]

    matched, missing = skill_gap(found_skills, required_skills)
    coverage_pct = (len(matched) / len(required_skills)) * 100 if required_skills else 0

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Target Role", target_role)
    c2.metric("Required Skills Matched", f"{len(matched)} / {len(required_skills)}", f"{coverage_pct:.0f}%")
    c3.metric("Missing Skills", len(missing))

    st.markdown("---")
    col_matched, col_missing = st.columns(2)

    with col_matched:
        st.markdown("### ✅ Skills You Already Have")
        if matched:
            st.markdown(
                "".join([f'<span class="skill-pill-matched">✓ {s}</span>' for s in matched]),
                unsafe_allow_html=True,
            )
        else:
            st.warning("None of the specific required skills for this role were identified in your resume.")

    with col_missing:
        st.markdown("### ❌ Missing Skills to Acquire")
        if missing:
            st.markdown(
                "".join([f'<span class="skill-pill-missing">✗ {s}</span>' for s in missing]),
                unsafe_allow_html=True,
            )
        else:
            st.success("🎉 Amazing! Your resume covers all required skills listed for this target role!")

    st.markdown("---")
    st.markdown("### 💡 Guidance & Analysis Insights")
    st.markdown(
        f"""
        - **Target Role Description:** {target_row['description']}
        - **Skill Coverage:** You possess **{len(matched)} out of {len(required_skills)}** core skills ({coverage_pct:.0f}%).
        - **Next Steps:** Review the **Learning Roadmap** tab to follow a curated week-by-week plan designed to bridge the {len(missing)} missing skills.
        """
    )


# -----------------------------------------------------------------------------
# PAGE 6: LEARNING ROADMAP
# -----------------------------------------------------------------------------
elif page == "🗺️ Learning Roadmap":
    st.markdown("## 🗺️ Personalized Learning Roadmap")
    st.markdown(f"Curated weekly study plan and portfolio projects for target role: **{st.session_state['target_role']}**.")

    if not st.session_state["uploaded_filename"]:
        st.warning("⚠️ No resume loaded yet. Please upload a resume or select a sample resume from the sidebar.")
        st.stop()

    target_role = st.session_state["target_role"]
    target_row = roles_df[roles_df["role"] == target_role].iloc[0]
    required_skills = target_row["skills"]
    found_skills = st.session_state["found_skills"]
    matched, missing = skill_gap(found_skills, required_skills)

    roadmap_steps = build_roadmap(missing, per_week=2)

    if missing:
        st.markdown(f"### 📅 Weekly Plan to Bridge {len(missing)} Missing Skills")
        for step in roadmap_steps:
            if ":" in step:
                week_title, details = step.split(":", 1)
                with st.expander(f"📌 {week_title}", expanded=True):
                    sub_items = details.split(" | ")
                    for sub in sub_items:
                        st.markdown(f"- {sub.strip()}")
            else:
                st.write(step)
    else:
        st.success(
            "🌟 Excellent work! Your resume covers all mandatory skills for this role. "
            "Focus on advanced end-to-end full-stack projects and deployment optimization to stand out."
        )

    st.markdown("---")
    st.markdown("### 🎯 Recommended Project Architecture for College Submissions")
    st.markdown(
        """
        When presenting this project or your candidate portfolio to faculty or technical interviewers:
        1. **End-to-End Pipeline:** Explain text extraction (PyPDF / python-docx), regex normalization, and PII scrubbing.
        2. **Explainable AI:** Emphasize that the 70/30 weighting balances explicit skill presence with semantic context.
        3. **Demonstrable Artifacts:** Showcase live container deployment, test coverage, and downloadable reports.
        """
    )


# -----------------------------------------------------------------------------
# PAGE 7: DOWNLOAD REPORT
# -----------------------------------------------------------------------------
elif page == "📄 Download Report":
    st.markdown("## 📄 Export & Download Candidate Analysis Report")
    st.markdown("Generate and download comprehensive evaluation reports for submission, documentation, or interview review.")

    if not st.session_state["uploaded_filename"]:
        st.warning("⚠️ No resume loaded yet. Please upload a resume or select a sample resume from the sidebar.")
        st.stop()

    target_role = st.session_state["target_role"]
    ranking = st.session_state["ranking_df"]
    target_row = ranking[ranking["role"] == target_role].iloc[0]
    found_skills = st.session_state["found_skills"]
    matched, missing = skill_gap(found_skills, roles_df.loc[roles_df["role"] == target_role, "skills"].iloc[0])
    top3 = [(r.role, r.score) for r in ranking.head(3).itertuples()]
    roadmap_steps = build_roadmap(missing)

    # Generate Reports in all three formats
    text_report = build_report(target_role, target_row["score"], found_skills, missing, top3, roadmap_steps)
    md_report = build_markdown_report(target_role, target_row["score"], found_skills, missing, top3, roadmap_steps)
    json_report = build_json_report(target_role, target_row["score"], found_skills, missing, top3, roadmap_steps)

    st.markdown("### 📥 Download Formats")
    d1, d2, d3 = st.columns(3)

    with d1:
        st.download_button(
            label="⬇️ Download Plain Text (.txt)",
            data=text_report,
            file_name=f"resume_analysis_{target_role.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            label="⬇️ Download Markdown (.md)",
            data=md_report,
            file_name=f"resume_analysis_{target_role.lower().replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with d3:
        st.download_button(
            label="⬇️ Download JSON Data (.json)",
            data=json_report,
            file_name=f"resume_analysis_{target_role.lower().replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("### 👁️ Report Preview")
    st.code(text_report, language="text")

