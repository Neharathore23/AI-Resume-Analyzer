"""Comprehensive Test Suite for AI Resume Analyzer & Job Recommendation System.
Covers all 10 project test cases required in Phase 5.
Run with: python tests/test_pipeline.py
"""
import io
import os
import sys
import pandas as pd

# Add project root and current directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from resume_parser import extract_text, validate, get_resume_metadata, ResumeError
from text_cleaner import clean_text, redact_personal_info
from skill_extractor import load_skill_dictionary, extract_skills, flatten
from job_matcher import load_roles, rank_roles, skill_gap
from roadmap_generator import build_roadmap, build_report, build_markdown_report, build_json_report

# Load datasets
skills_df = load_skill_dictionary()
roles_df = load_roles()


def test_1_valid_pdf_resume():
    """Test Case 1: Valid PDF resume parsing and extraction."""
    pdf_path = os.path.join(BASE_DIR, "sample_resumes", "resume_A_data_analyst.pdf")
    assert os.path.exists(pdf_path), f"Sample PDF not found at {pdf_path}"
    with open(pdf_path, "rb") as f:
        data = f.read()
    raw_text = extract_text(os.path.basename(pdf_path), data)
    assert len(raw_text.strip()) >= 50, "Extracted PDF text is too short"
    assert "Data Analyst" in raw_text or "Python" in raw_text
    meta = get_resume_metadata("resume_A_data_analyst.pdf", data, raw_text)
    assert meta["extension"] == "PDF"
    assert meta["word_count"] > 10
    print("  [PASS] Test Case 1: Valid PDF resume extraction passed.")


def test_2_valid_docx_resume():
    """Test Case 2: Valid DOCX resume parsing and extraction."""
    docx_path = os.path.join(BASE_DIR, "sample_resumes", "resume_B_ml_engineer.docx")
    assert os.path.exists(docx_path), f"Sample DOCX not found at {docx_path}"
    with open(docx_path, "rb") as f:
        data = f.read()
    raw_text = extract_text(os.path.basename(docx_path), data)
    assert len(raw_text.strip()) >= 50, "Extracted DOCX text is too short"
    assert "Machine Learning" in raw_text
    meta = get_resume_metadata("resume_B_ml_engineer.docx", data, raw_text)
    assert meta["extension"] == "DOCX"
    assert meta["word_count"] > 10
    print("  [PASS] Test Case 2: Valid DOCX resume extraction passed.")


def test_3_invalid_file_format():
    """Test Case 3: Invalid file format rejection."""
    try:
        validate("candidate_resume.png", 5000)
        assert False, "Failed to reject invalid file extension (.png)"
    except ResumeError as e:
        assert "Unsupported file type" in str(e)
    try:
        validate("document.exe", 1000)
        assert False, "Failed to reject executable file extension (.exe)"
    except ResumeError as e:
        assert "Unsupported file type" in str(e)
    print("  [PASS] Test Case 3: Invalid file format rejection passed.")


def test_4_empty_resume():
    """Test Case 4: Empty or unreadable resume detection."""
    try:
        extract_text("empty.docx", b"PK\x03\x04" + b"\x00" * 30)
        assert False, "Failed to detect corrupted/empty document"
    except ResumeError as e:
        assert ("Could not read the file" in str(e)) or ("No readable text found" in str(e))
    print("  [PASS] Test Case 4: Empty resume rejection passed.")


def test_5_large_resume():
    """Test Case 5: Oversized file handling (> 5MB)."""
    large_size = 6 * 1024 * 1024  # 6 MB
    try:
        validate("huge_resume.pdf", large_size)
        assert False, "Failed to reject file exceeding MAX_FILE_SIZE_MB"
    except ResumeError as e:
        assert "File too large" in str(e)
    print("  [PASS] Test Case 5: Large resume validation passed.")


def test_6_resume_with_no_detectable_skills():
    """Test Case 6: Resume containing no identifiable technical skills."""
    non_tech_text = (
        "I am an enthusiastic and highly motivated professional with extensive experience "
        "in general customer care, office administration, and interpersonal communication. "
        "Dedicated to team synergy, positive attitude, and workplace punctuality."
    )
    cleaned = clean_text(non_tech_text)
    found_dict = extract_skills(cleaned, skills_df)
    found = flatten(found_dict)
    assert len(found) == 0, f"Expected 0 skills, but found: {found}"
    
    # rank_roles must execute safely without zero-division error
    ranking = rank_roles(cleaned, found, roles_df)
    assert not ranking.empty
    assert len(ranking) == len(roles_df)
    assert (ranking["score"] >= 0).all()
    print("  [PASS] Test Case 6: Resume with no detectable skills handled safely.")


def test_7_cplusplus_csharp_dotnet_cicd_extraction():
    """Test Case 7: Exact token preservation and extraction for C++, C#, .NET, CI/CD."""
    sample_text = "Proficient in C++, C#, .NET, and CI/CD pipelines alongside Python."
    cleaned = clean_text(sample_text)
    
    # Verify cleaned string preserved tokens
    assert "c++" in cleaned, "c++ was not preserved in cleaned text"
    assert "c#" in cleaned, "c# was not preserved in cleaned text"
    assert ".net" in cleaned, ".net was not preserved in cleaned text"
    assert "ci/cd" in cleaned, "ci/cd was not preserved in cleaned text"
    
    # Verify skill extraction detects all 4 skills
    found_dict = extract_skills(cleaned, skills_df)
    found = flatten(found_dict)
    assert "C++" in found, f"C++ missing from detected skills: {found}"
    assert "C#" in found, f"C# missing from detected skills: {found}"
    assert ".NET" in found, f".NET missing from detected skills: {found}"
    assert "CI/CD" in found, f"CI/CD missing from detected skills: {found}"
    print("  [PASS] Test Case 7: C++, C#, .NET, CI/CD tokens preserved and extracted successfully.")


def test_8_job_recommendation_accuracy():
    """Test Case 8: Recommendation accuracy across all sample resumes (PDF and DOCX)."""
    cases_path = os.path.join(BASE_DIR, "tests", "test_cases.csv")
    df = pd.read_csv(cases_path, dtype=str).fillna("")
    
    for i, r in df.iterrows():
        sample_file = os.path.join(BASE_DIR, "sample_resumes", r["test_resume"])
        assert os.path.exists(sample_file), f"Sample file not found: {sample_file}"
        with open(sample_file, "rb") as f:
            data = f.read()
        raw = extract_text(r["test_resume"], data)
        clean = clean_text(raw)
        found = flatten(extract_skills(clean, skills_df))
        ranking = rank_roles(clean, found, roles_df)
        
        top_role = ranking.iloc[0]["role"]
        top_score = ranking.iloc[0]["score"]
        expected = r["expected_top_role"]
        
        df.loc[i, "actual_top_role"] = top_role
        status = "PASS" if top_role == expected else "REVIEW"
        df.loc[i, "comments"] = f"{len(found)} skills; score {top_score:.1f}; {status}"
        
        assert top_role == expected, (
            f"Accuracy failure for {r['test_resume']}: expected '{expected}', got '{top_role}'"
        )
    
    # Save back updated test cases
    df.to_csv(cases_path, index=False)
    # Also save to ai_resume_analyzer subfolder if present
    sub_cases = os.path.join(BASE_DIR, "ai_resume_analyzer", "tests", "test_cases.csv")
    if os.path.exists(os.path.dirname(sub_cases)):
        df.to_csv(sub_cases, index=False)
    print("  [PASS] Test Case 8: Job recommendation accuracy 100% verified against ground truth.")


def test_9_missing_skill_identification():
    """Test Case 9: Skill gap analysis logic (matched vs missing skills)."""
    candidate_skills = ["Python", "SQL", "Pandas"]
    required_skills = ["Python", "SQL", "Excel", "Pandas", "Power BI", "Statistics"]
    matched, missing = skill_gap(candidate_skills, required_skills)
    
    assert set(matched) == {"Python", "SQL", "Pandas"}
    assert set(missing) == {"Excel", "Power BI", "Statistics"}
    assert len(matched) + len(missing) == len(required_skills)
    print("  [PASS] Test Case 9: Missing skill identification passed.")


def test_10_report_download():
    """Test Case 10: Analysis report generation in text, markdown, and JSON formats."""
    target = "Data Analyst"
    score = 85.5
    found = ["Python", "SQL", "Pandas", "Excel"]
    missing = ["Power BI", "Statistics"]
    top_roles = [("Data Analyst", 85.5), ("Data Scientist", 78.0), ("Python Developer", 70.2)]
    roadmap = build_roadmap(missing)
    
    # Text Report
    text_report = build_report(target, score, found, missing, top_roles, roadmap)
    assert "AI RESUME ANALYZER & JOB RECOMMENDATION SYSTEM" in text_report
    assert f"Target Role    : {target}" in text_report
    assert "Power BI" in text_report
    assert "Disclaimer" in text_report or "DISCLAIMER" in text_report
    
    # Markdown Report
    md_report = build_markdown_report(target, score, found, missing, top_roles, roadmap)
    assert "# 📄 AI Resume Analyzer" in md_report
    assert "Data Analyst" in md_report
    
    # JSON Report
    json_report = build_json_report(target, score, found, missing, top_roles, roadmap)
    assert '"target_role": "Data Analyst"' in json_report
    assert '"match_score": 85.5' in json_report
    print("  [PASS] Test Case 10: Report generation (Text, Markdown, JSON) passed.")


def run_all_tests():
    print("=" * 70)
    print("STARTING TEST SUITE: AI RESUME ANALYZER & JOB RECOMMENDATION SYSTEM")
    print("=" * 70)
    test_1_valid_pdf_resume()
    test_2_valid_docx_resume()
    test_3_invalid_file_format()
    test_4_empty_resume()
    test_5_large_resume()
    test_6_resume_with_no_detectable_skills()
    test_7_cplusplus_csharp_dotnet_cicd_extraction()
    test_8_job_recommendation_accuracy()
    test_9_missing_skill_identification()
    test_10_report_download()
    print("=" * 70)
    print("ALL 10 TEST CASES PASSED SUCCESSFULLY (10/10)!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
