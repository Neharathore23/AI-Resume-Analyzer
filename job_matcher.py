"""Modules 4, 5, 6 - role dataset, TF-IDF/cosine matching, skill-gap analysis.

Match score (0-100) = 70% skill coverage + 30% TF-IDF cosine similarity.
  * coverage  = required role skills found in resume / total required skills
  * cosine    = similarity of resume text vs role text (skills + description)
Scores are estimates for guidance only, not recruiter decisions."""
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from text_cleaner import clean_text
except ImportError:
    from .text_cleaner import clean_text

W_COVERAGE, W_TFIDF = 0.7, 0.3


def load_roles(path=None) -> pd.DataFrame:
    """Load job roles dataset with robust path resolution."""
    if path is None:
        if os.path.exists("data/job_roles.csv"):
            path = "data/job_roles.csv"
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_dir, "data", "job_roles.csv")
    df = pd.read_csv(path)
    df["skills"] = df["required_skills"].str.split("|").apply(lambda xs: [x.strip() for x in xs])
    return df


def skill_gap(found_skills, required_skills):
    """Determine matched and missing skills given detected and required skills."""
    have = {s.lower() for s in found_skills}
    matched = [s for s in required_skills if s.lower() in have]
    missing = [s for s in required_skills if s.lower() not in have]
    return matched, missing


def rank_roles(clean_resume: str, found_skills, roles: pd.DataFrame) -> pd.DataFrame:
    """
    Rank all roles based on weighted combination of Skill Coverage (70%) and TF-IDF Cosine Similarity (30%).
    Handles edge cases like empty resumes safely.
    """
    clean_resume = (clean_resume or "").strip()
    
    if not clean_resume:
        rows = []
        for r in roles.itertuples():
            matched, missing = skill_gap(found_skills, r.skills)
            rows.append({
                "role": r.role,
                "score": 0.0,
                "coverage": 0.0,
                "tfidf_cosine": 0.0,
                "matched": matched,
                "missing": missing,
                "explanation": "No readable resume content provided for matching.",
            })
        return pd.DataFrame(rows)

    role_docs = [clean_text(" ".join(r.skills) + " " + r.description) for r in roles.itertuples()]
    vec = TfidfVectorizer(token_pattern=r"[a-z0-9+#.\-/]+", ngram_range=(1, 2), sublinear_tf=True)
    matrix = vec.fit_transform([clean_resume] + role_docs)
    cos = cosine_similarity(matrix[0], matrix[1:]).flatten()

    rows = []
    for r, c in zip(roles.itertuples(), cos):
        matched, missing = skill_gap(found_skills, r.skills)
        coverage = len(matched) / len(r.skills) if r.skills else 0.0
        c_val = float(c)
        score = round(100 * (W_COVERAGE * coverage + W_TFIDF * c_val), 1)
        cov_pct = round(100 * coverage, 1)
        cos_val = round(c_val, 3)
        
        explanation = (
            f"Matches {len(matched)} of {len(r.skills)} required skills ({cov_pct:.0f}% coverage). "
            f"Profile semantic similarity is {cos_val * 100:.1f}%."
        )
        
        rows.append({
            "role": r.role,
            "score": score,
            "coverage": cov_pct,
            "tfidf_cosine": cos_val,
            "matched": matched,
            "missing": missing,
            "explanation": explanation,
        })
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)

