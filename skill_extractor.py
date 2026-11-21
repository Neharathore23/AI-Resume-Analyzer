"""Module 3 - controlled-dictionary skill extraction with categories."""
import os
import re
import pandas as pd


def load_skill_dictionary(path=None) -> pd.DataFrame:
    """Load skill dictionary with graceful path resolution."""
    if path is None:
        if os.path.exists("data/skill_dictionary.csv"):
            path = "data/skill_dictionary.csv"
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_dir, "data", "skill_dictionary.csv")
    return pd.read_csv(path).fillna("")


def _compile(df: pd.DataFrame):
    patterns = {}
    for _, r in df.iterrows():
        aliases = {
            r["skill"].lower(),
            *[a.strip().lower() for a in r["aliases"].split("|") if a.strip()],
        }
        alt = "|".join(re.escape(a) for a in sorted(aliases, key=len, reverse=True))
        # Boundaries that treat + # as part of a word so "c" never matches inside "c++"
        patterns[r["skill"]] = re.compile(
            rf"(?<![a-z0-9+#]){'(?:' + alt + ')'}(?![a-z0-9+#])"
        )
    return patterns


def extract_skills(clean_text_input: str, skill_df: pd.DataFrame) -> dict:
    """Return {category: [skills]} for skills found in the cleaned text."""
    if not clean_text_input or skill_df.empty:
        return {}
    found = {}
    patterns = _compile(skill_df)
    for skill, pat in patterns.items():
        if pat.search(clean_text_input):
            cat = skill_df.loc[skill_df["skill"] == skill, "category"].iloc[0]
            found.setdefault(cat, []).append(skill)
    return found


def flatten(found: dict) -> list:
    """Flatten categorized skill dictionary into a sorted unique list of skills."""
    return sorted({s for skills in found.values() for s in skills})

