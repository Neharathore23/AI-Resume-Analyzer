# System Architecture & Technical Design

## 1. High-Level Architecture Flowchart

```mermaid
flowchart TD
    subgraph UI["Frontend Layer (Streamlit & Custom CSS)"]
        UI_Home["Home Dashboard (Overview & Quickstart)"]
        UI_Upload["Resume Ingestion (PDF / DOCX)"]
        UI_Analysis["Skill Analytics & Category Visuals"]
        UI_Match["Job Recommendations & Podium"]
        UI_Gap["Skill Gap Benchmarking"]
        UI_Roadmap["Weekly Portfolio Learning Plan"]
        UI_Report["Report Generator (TXT, MD, JSON)"]
    end

    subgraph Core["Processing & NLP Pipeline (In-Memory)"]
        P_Parse["resume_parser.py<br/>Type & Size Validation<br/>pypdf / python-docx"]
        P_Clean["text_cleaner.py<br/>Responsible AI PII Redaction<br/>Domain Token Normalization"]
        P_Extract["skill_extractor.py<br/>Controlled Regex Engine<br/>Boundary Detection"]
        P_Match["job_matcher.py<br/>TF-IDF Vectorization<br/>Cosine Similarity<br/>Weighted Formula"]
        P_Roadmap["roadmap_generator.py<br/>Weekly Curriculum<br/>Portfolio Projects"]
    end

    subgraph Data["Knowledge Base & Datasets"]
        D_Skills[("data/skill_dictionary.csv<br/>65+ Categorized Skills & Aliases")]
        D_Roles[("data/job_roles.csv<br/>8 Tech Job Profiles & Descriptions")]
    end

    UI_Upload -->|In-memory Bytes| P_Parse
    P_Parse -->|Extracted Text| P_Clean
    P_Clean -->|Cleaned Text| P_Extract
    D_Skills -->|Skill Patterns| P_Extract
    P_Extract -->|Detected Skills| P_Match
    D_Roles -->|Role Profiles| P_Match
    P_Clean -->|Document Vectors| P_Match
    P_Match -->|Ranked Roles & Gaps| P_Roadmap
    P_Extract --> UI_Analysis
    P_Match --> UI_Match
    P_Match --> UI_Gap
    P_Roadmap --> UI_Roadmap
    P_Roadmap --> UI_Report
```

## 2. Match Scoring Algorithm

The matching algorithm balances explicit skill presence with semantic context:

$$\text{Match Score} = 0.70 \times \text{Skill Coverage} + 0.30 \times \text{TF-IDF Cosine Similarity}$$

Where:
- **Skill Coverage ($70\%$):** 
  $$\text{Coverage} = \frac{\text{Required Skills Found in Resume}}{\text{Total Required Skills for Role}} \times 100$$
- **TF-IDF Cosine Similarity ($30\%$):**
  $$\text{Cosine Similarity} = \frac{\mathbf{v}_{\text{resume}} \cdot \mathbf{v}_{\text{role}}}{\|\mathbf{v}_{\text{resume}}\| \|\mathbf{v}_{\text{role}}\|}$$
  Computed over unigrams and bigrams $(1, 2)$ with sublinear term-frequency scaling.

## 3. Responsible AI & Data Privacy Guardrails
1. **Zero Disk Storage:** Resumes are parsed in RAM (`io.BytesIO`) and discarded upon session closure.
2. **PII Removal:** Emails, phone numbers, and URLs are stripped before tokenization.
3. **No Protected Attributes:** The engine never parses or scores candidate gender, age, race, religion, photo, or marital status.
4. **Advisory Tooling:** Clear disclaimers reinforce that match scores are educational guidelines, not automated hiring gates.
