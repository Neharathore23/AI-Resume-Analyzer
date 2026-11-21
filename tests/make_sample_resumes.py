"""Generates anonymised sample resumes in DOCX and PDF formats for testing and demonstration."""
import os
from docx import Document


def make_simple_pdf(filename, text_lines):
    """Minimal standard valid PDF 1.4 generator in pure Python without external binary dependencies."""
    stream = "BT /F1 11 Tf 50 740 Td 15 TL\n"
    for line in text_lines:
        clean = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream += f"({clean}) '\n"
    stream += "ET"
    stream_bytes = stream.encode("latin1", errors="replace")
    length = len(stream_bytes)

    obj1 = b"<< /Type /Catalog /Pages 2 0 R >>"
    obj2 = b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
    obj3 = (
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
    )
    obj4 = f"<< /Length {length} >>\nstream\n".encode("latin1") + stream_bytes + b"\nendstream"
    obj5 = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"

    body = [obj1, obj2, obj3, obj4, obj5]
    offsets = []
    output = bytearray(b"%PDF-1.4\n")
    for i, obj in enumerate(body, 1):
        offsets.append(len(output))
        output.extend(f"{i} 0 obj\n".encode("latin1") + obj + b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(body)+1}\n0000000000 65535 f \n".encode("latin1"))
    for off in offsets:
        output.extend(f"{off:010d} 00000 n \n".encode("latin1"))
    output.extend(
        f"trailer\n<< /Size {len(body)+1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("latin1")
    )

    with open(filename, "wb") as f:
        f.write(output)


SAMPLES = {
    "resume_A_data_analyst": {
        "title": "Alex Taylor - Data Analyst",
        "body": [
            "Contact: candidate.a@example.com | +91 98765 43210 | Bangalore, India",
            "LinkedIn: linkedin.com/in/alextaylor-data | GitHub: github.com/alextaylor",
            "Education: B.Sc. Statistics & Mathematics, 2024",
            "Core Skills: Python, SQL, Excel, Pandas, Power BI, Tableau, Data Visualization, Data Cleaning, Statistics, MySQL.",
            "Professional Experience: Data Analyst Intern at InsightCorp (6 months).",
            "  - Extracted and cleaned multi-source business data using SQL and Pandas.",
            "  - Built interactive executive sales dashboards in Power BI and Excel.",
            "  - Conducted statistical hypothesis testing to evaluate marketing campaign performance.",
            "Projects:",
            "  - Retail Analytics Dashboard: Built automated SQL queries and Power BI dashboard.",
            "  - Customer Churn Analysis: Data cleaning, exploratory data analysis using Pandas and Matplotlib.",
        ],
    },
    "resume_B_ml_engineer": {
        "title": "Jordan Reed - Machine Learning Engineer",
        "body": [
            "Contact: jordan.reed@example.com | +91 91234 56789 | Hyderabad, India",
            "LinkedIn: linkedin.com/in/jordanreed-ml | GitHub: github.com/jordanreed",
            "Education: B.Tech Computer Science and Engineering, 2024",
            "Core Skills: Python, Machine Learning, scikit-learn, Pandas, NumPy, FastAPI, Docker, MLflow, Git, GitHub, Model Deployment, SQL.",
            "Professional Experience: Machine Learning Intern at AI Dynamics (6 months).",
            "  - Trained predictive regression and classification models using scikit-learn pipelines.",
            "  - Containerized inference applications using Docker and automated Git workflows.",
            "  - Tracked model experiments, parameters, and metrics using MLflow.",
            "Projects:",
            "  - Production ML Microservice: Deployed scikit-learn model as a REST API with FastAPI and Docker.",
            "  - Credit Risk Prediction: Feature engineering, hyperparameter tuning, model deployment on cloud.",
        ],
    },
    "resume_C_nlp_engineer": {
        "title": "Samira Khan - NLP Engineer",
        "body": [
            "Contact: samira.khan@example.com | +91 99887 76655 | Pune, India",
            "LinkedIn: linkedin.com/in/samirakhan-nlp | GitHub: github.com/samirakhan",
            "Education: M.Tech Artificial Intelligence, 2024",
            "Core Skills: Python, NLP, Transformers, Hugging Face, spaCy, NLTK, PyTorch, Deep Learning, Sentence Transformers, REST API.",
            "Professional Experience: NLP Research Intern at Cognition Labs (8 months).",
            "  - Fine-tuned BERT and RoBERTa models for multi-class domain text classification using Hugging Face.",
            "  - Built named entity recognition (NER) pipelines using spaCy and tokenizers.",
            "  - Implemented semantic document search using Sentence Transformers and PyTorch.",
            "Projects:",
            "  - Semantic Resume Parser: Extracted entities from raw documents using spaCy and Transformers.",
            "  - Customer Feedback Analyzer: Text preprocessing, sentiment classification using PyTorch.",
        ],
    },
    "resume_D_fullstack_engineer": {
        "title": "Morgan Lee - Software Engineer",
        "body": [
            "Contact: morgan.lee@example.com | +91 98111 22233 | Delhi, India",
            "LinkedIn: linkedin.com/in/morganlee-dev | GitHub: github.com/morganlee",
            "Education: B.Tech Computer Science, 2023",
            "Core Skills: Python, C++, C#, .NET, CI/CD, SQL, OOP, REST API, Unit Testing, Docker, Git, Flask.",
            "Professional Experience: Junior Software Engineer at TechSystems (1 year).",
            "  - Developed backend REST API endpoints using Python, Flask, C#, and .NET.",
            "  - Implemented core system algorithms in C++ following object-oriented design (OOP).",
            "  - Automated continuous integration and deployment with CI/CD GitHub Actions.",
            "  - Wrote comprehensive unit tests and regression test suites with pytest.",
            "Projects:",
            "  - Distributed Task Scheduler: Built in C++ and Python with Docker containerization.",
            "  - Enterprise API Gateway: Built using C# and .NET with full CI/CD deployment pipeline.",
        ],
    },
}


def generate_all():
    dest_dirs = ["sample_resumes", os.path.join("ai_resume_analyzer", "sample_resumes")]
    for target_dir in dest_dirs:
        os.makedirs(target_dir, exist_ok=True)
        for name, data in SAMPLES.items():
            # 1. Generate DOCX
            docx_path = os.path.join(target_dir, f"{name}.docx")
            doc = Document()
            doc.add_heading(data["title"], 1)
            for line in data["body"]:
                doc.add_paragraph(line)
            doc.save(docx_path)

            # 2. Generate PDF
            pdf_path = os.path.join(target_dir, f"{name}.pdf")
            pdf_lines = [data["title"]] + data["body"]
            make_simple_pdf(pdf_path, pdf_lines)

    print(f"Successfully generated {len(SAMPLES)} DOCX and {len(SAMPLES)} PDF sample resumes in {dest_dirs}!")


if __name__ == "__main__":
    generate_all()

