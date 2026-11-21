"""Module 6 - rule-based learning roadmap + downloadable reports."""
import json
from datetime import date

# Comprehensive learning guide mapping skills to actionable learning objectives
TOPICS = {
    # Programming & Foundations
    "Python": "Python mastery: data structures, list comprehensions, generators, type hinting, and virtual environments",
    "Java": "Java fundamentals: object-oriented programming, collections framework, multi-threading, and JVM memory model",
    "C++": "C++ modern syntax: pointers, memory management, STL containers, templates, and RAII patterns",
    "C#": "C# & .NET ecosystem: LINQ, async/await, delegates, and entity framework basics",
    ".NET": ".NET platform: building RESTful web APIs with ASP.NET Core and dependency injection",
    "JavaScript": "Modern JavaScript: ES6+ syntax, Promises, async/await, DOM manipulation, and Node.js runtime",
    "TypeScript": "TypeScript fundamentals: type annotations, interfaces, generics, and strict type checking",
    "OOP": "Object-oriented programming: encapsulation, inheritance, polymorphism, and SOLID design principles",
    "Unit Testing": "Automated testing: pytest fixtures, parameterized tests, test-driven development (TDD), and coverage reporting",
    "Agile": "Agile software development: Scrum rituals, sprint planning, Jira issue tracking, and backlog grooming",
    # Databases & Big Data
    "SQL": "SQL queries: inner/outer joins, aggregate functions, subqueries, indexing, and window functions",
    "MySQL": "MySQL administration: relational schema design, foreign keys, transactions, and query optimization",
    "PostgreSQL": "PostgreSQL: advanced data types (JSONB), indexing (GIN/GiST), views, and stored procedures",
    "MongoDB": "NoSQL with MongoDB: document data modeling, aggregation pipelines, and indexing with PyMongo",
    "SQLite": "Embedded database development: lightweight database design and SQLite integration in Python apps",
    "Spark": "Distributed computing with PySpark: resilient distributed datasets (RDDs), DataFrames, and Spark SQL",
    "Airflow": "Workflow orchestration: Apache Airflow DAGs, task scheduling, operators, and data pipeline monitoring",
    "ETL": "ETL pipelines: data extraction from APIs/databases, transformations, validation, and loading into warehouses",
    # Tools & Development
    "Git": "Version control: branching strategies, merge conflict resolution, rebasing, and pull request workflows",
    "GitHub": "Collaborative development: repository management, GitHub Actions, code reviews, and project boards",
    "Jupyter": "Interactive notebook workflows: exploratory data analysis, parameterization, and notebook export",
    "Linux": "Linux command line: bash scripting, file permissions, process management, and SSH server administration",
    "Excel": "Advanced spreadsheet analysis: VLOOKUP/XLOOKUP, INDEX-MATCH, pivot tables, and dashboard design",
    "Power BI": "Business intelligence: Power BI data modeling, DAX measures, relationships, and interactive report publishing",
    "Tableau": "Data storytelling: Tableau dimensions/measures, calculated fields, parameters, and visual dashboards",
    # Data Science & Analysis
    "Pandas": "Pandas data wrangling: DataFrame filtering, grouping, reshaping (melt/pivot), and merging multi-source data",
    "NumPy": "Scientific computing: multi-dimensional arrays, vectorization, broadcasting, and matrix operations",
    "Statistics": "Statistical inference: probability distributions, hypothesis testing (t-test/ANOVA), p-values, and confidence intervals",
    "Data Cleaning": "Data preprocessing: missing value imputation, outlier detection with IQR/Z-score, and data type formatting",
    "Feature Engineering": "Feature creation: one-hot encoding, target encoding, standard/robust scaling, and PCA dimensionality reduction",
    "Data Visualization": "Visual analytics: best practices for chart selection, distribution plots, heatmaps, and publication styling",
    "Time Series": "Temporal data analysis: trend/seasonality decomposition, ARIMA, SARIMA, and forecasting metrics (RMSE/MAE)",
    "Matplotlib": "Plotting in Python: subplots, figure customization, styling, and multi-axis visualizations",
    "Plotly": "Interactive dashboards: Plotly Express charts, custom hover templates, callbacks, and responsive web visuals",
    "Seaborn": "Statistical visualization: pairplots, violin plots, correlation heatmaps, and regression plots",
    # Machine Learning & MLOps
    "Machine Learning": "Core ML algorithms: linear/logistic regression, decision trees, random forests, and bias-variance tradeoff",
    "scikit-learn": "Production scikit-learn: Pipeline objects, ColumnTransformer, GridSearchCV, and model evaluation metrics",
    "XGBoost": "Gradient boosting: XGBoost, LightGBM, hyperparameter tuning, early stopping, and feature importance analysis",
    "MLflow": "MLOps lifecycle: experiment tracking, artifact logging, model versioning, and registry deployment",
    "Model Deployment": "Model serving: serializing models (pickle/joblib/ONNX), building inference endpoints, and monitoring drift",
    # Deep Learning & AI
    "Deep Learning": "Deep neural networks: backpropagation, activation functions, optimizers (Adam), and dropout regularization",
    "PyTorch": "PyTorch framework: tensors, custom Dataset/DataLoader classes, neural network modules, and GPU training loops",
    "TensorFlow": "TensorFlow 2 & Keras: Sequential/Functional APIs, callbacks, TensorBoard, and model evaluation",
    "Keras": "Rapid prototyping: Keras layers, custom loss functions, transfer learning, and fine-tuning pretrained models",
    # NLP & GenAI
    "NLP": "Natural Language Processing: tokenization, lemmatization, stopword removal, TF-IDF, and word embeddings",
    "spaCy": "Industrial NLP: part-of-speech tagging, dependency parsing, and custom Named Entity Recognition (NER) pipelines",
    "NLTK": "Text processing: regular expression tokenization, stemming, corpus analysis, and sentiment analysis",
    "Transformers": "Transformer architectures: self-attention mechanism, BERT encoder models, and GPT autoregressive generation",
    "Hugging Face": "Hugging Face ecosystem: transformers library, Datasets, Trainer API, and model hub fine-tuning",
    "Sentence Transformers": "Dense text embeddings: bi-encoders, semantic search, cosine similarity ranking, and SBERT models",
    "LLM": "Large Language Models: prompting strategies, system instructions, temperature tuning, and hallucination reduction",
    "RAG": "Retrieval-Augmented Generation: document chunking, dense vector retrieval, hybrid search, and context grounding",
    "Prompt Engineering": "Advanced prompting: few-shot exemplars, chain-of-thought (CoT), output structuring (JSON), and validation",
    "LangChain": "LLM orchestration: prompts, Document loaders, TextSplitters, retrieval QA chains, and memory modules",
    "Vector Database": "Vector storage: FAISS, ChromaDB, Pinecone, similarity index creation, and top-k approximate nearest neighbor search",
    # Computer Vision
    "Computer Vision": "Vision fundamentals: color spaces, image filtering, edge detection (Canny), and spatial transformations",
    "OpenCV": "OpenCV library: video capture, contour extraction, bounding boxes, object tracking, and morphological operations",
    "CNN": "Convolutional Neural Networks: convolution kernels, pooling layers, ResNet architectures, and image classification",
    "YOLO": "Real-time object detection: YOLOv8 architecture, custom dataset annotation, training, and inference pipelines",
    "Image Processing": "Image augmentation: Albumentations library, normalization, synthetic generation, and noise reduction",
    # Backend & DevOps
    "FastAPI": "High-performance APIs: FastAPI asynchronous routes, Pydantic schemas, Swagger UI, and background tasks",
    "Flask": "Lightweight web development: Flask blueprints, routing, request parsing, and template rendering",
    "Django": "Enterprise web applications: Django ORM, admin dashboard, user authentication, and REST framework",
    "REST API": "API architecture: HTTP verbs, status codes, resource-oriented URI design, JSON contracts, and error handling",
    "Streamlit": "Data applications: interactive widgets, session state management, caching, and custom component layout",
    "Docker": "Containerization: writing optimized Dockerfiles, multi-stage builds, container isolation, and docker-compose",
    "Kubernetes": "Container orchestration: Pods, Deployments, Services, ConfigMaps, and cluster scalability",
    "CI/CD": "Continuous Integration & Delivery: GitHub Actions workflows, automated testing on push, and automated deployment",
    "AWS": "Amazon Web Services: Amazon EC2, S3 bucket storage, SageMaker model training, and IAM permissions",
    "Azure": "Microsoft Azure: Azure App Service, Azure Blob Storage, and Azure Cognitive Services",
    "GCP": "Google Cloud Platform: Google Compute Engine, Cloud Storage, Vertex AI, and Cloud Run serverless deployment",
    "Cloud Deployment": "Cloud hosting: deploying web apps to Streamlit Community Cloud, Render, or cloud VMs with custom domains",
    "HTML": "Semantic HTML5: document structure, accessible form inputs, and SEO-friendly tags",
    "CSS": "Modern styling: Flexbox, CSS Grid layouts, media queries for responsiveness, and CSS variables",
}

# Practical portfolio projects suggested for missing skills
PROJECTS = {
    "Python": "Build an automated CLI tool that cleans and standardizes messy CSV datasets with error logging.",
    "SQL": "Design a relational database schema for an e-commerce platform and write 15 analytical window-function queries.",
    "Power BI": "Create an interactive 3-page executive sales dashboard analyzing profit margins, regional trends, and churn.",
    "Excel": "Build a financial modeling workbook with dynamic XLOOKUPs, data validation rules, and automated summary pivot charts.",
    "Pandas": "Perform end-to-end exploratory data analysis on a real-world healthcare dataset and export insights.",
    "Statistics": "Conduct A/B testing analysis on marketing data, calculate p-values, confidence intervals, and interpret significance.",
    "Data Cleaning": "Build an automated data cleaning script that handles missing values, detects anomalies, and normalizes columns.",
    "Data Visualization": "Create an interactive multi-chart visual report using Plotly and publish it as a web page.",
    "Feature Engineering": "Engineer 10+ behavioral and aggregated features on a churn prediction dataset to boost model F1-score.",
    "Machine Learning": "Build and compare 4 classification models with cross-validation and hyperparameter tuning.",
    "scikit-learn": "Create an end-to-end scikit-learn Pipeline with automated preprocessing and hyperparameter search.",
    "FastAPI": "Develop a REST API with FastAPI and Pydantic validation that serves predictions from a trained ML model.",
    "Docker": "Containerize a Python web application with a multi-stage Dockerfile and test it running on localhost.",
    "MLflow": "Integrate MLflow into a training pipeline to track parameters, metrics, confusion matrices, and register best models.",
    "Model Deployment": "Deploy an interactive machine learning application live to Streamlit Community Cloud.",
    "Deep Learning": "Train a multi-layer neural network on tabular or image data using early stopping and learning rate scheduling.",
    "PyTorch": "Implement a custom convolutional neural network in PyTorch and train it with GPU acceleration.",
    "NLP": "Build a text classification system using TF-IDF and Logistic Regression to categorize support tickets.",
    "Transformers": "Fine-tune a pretrained Hugging Face BERT model on sentiment analysis with custom evaluation metrics.",
    "Hugging Face": "Use the Hugging Face Pipeline API to implement sentiment analysis, summarization, and zero-shot classification.",
    "LLM": "Build an intelligent assistant using OpenAI/Gemini API with structured JSON output and prompt guardrails.",
    "RAG": "Create a Document Q&A application using LangChain, ChromaDB vector store, and document chunking.",
    "LangChain": "Build a multi-step conversational agent that queries an external API and summarizes the findings.",
    "Vector Database": "Index 1,000 document embeddings into ChromaDB/FAISS and benchmark similarity retrieval latency.",
    "Prompt Engineering": "Design and evaluate few-shot and chain-of-thought prompts to extract structured entities from unstructured resumes.",
    "OpenCV": "Build a real-time webcam face and motion detection application using OpenCV Haar cascades and contours.",
    "CNN": "Train a convolutional neural network on medical images (e.g. chest X-rays) using transfer learning.",
    "YOLO": "Annotate a custom dataset and train a YOLOv8 object detector to recognize specific objects in images.",
    "Image Processing": "Build an automated image preprocessing pipeline that resizes, augments, and normalizes computer vision data.",
    "Git": "Create a public GitHub repository following git-flow branching, write clear commits, and draft a professional README.",
    "REST API": "Design and consume a RESTful API with authentication tokens and rate-limiting handling in Python.",
    "Flask": "Build a lightweight web portal using Flask routes, Jinja templates, and form handling.",
    "OOP": "Design an object-oriented library management system implementing clean design patterns and unit tests.",
    "Unit Testing": "Write a 15-test pytest test suite with test fixtures, mocks, and parameterized test cases.",
    "Streamlit": "Build and deploy an interactive multi-page data analytics web application with Plotly charts.",
    "CI/CD": "Set up a GitHub Actions workflow that automatically runs flake8 linting and pytest tests on every push.",
    "C++": "Build a high-performance multithreaded numerical computation utility in C++.",
    "C#": "Develop an ASP.NET Core web service with CRUD endpoints and SQLite integration.",
    ".NET": "Build and test a REST API with ASP.NET Core Web API and Swagger documentation.",
}


def build_roadmap(missing, per_week=2):
    """
    Group missing skills into weekly learning goals.
    Each week presents specific theoretical topics and hands-on portfolio projects.
    """
    if not missing:
        return [
            "Outstanding skill match! Your resume covers all core required skills. Focus on building advanced full-stack portfolio projects to demonstrate practical mastery."
        ]
    plan = []
    for i in range(0, len(missing), per_week):
        chunk = missing[i : i + per_week]
        week_num = i // per_week + 1
        items = []
        for s in chunk:
            topic = TOPICS.get(s, f"{s}: study foundational concepts and practical implementations")
            project = PROJECTS.get(s, f"Build a small portfolio project applying {s} in practice.")
            items.append(f"{topic} (Project: {project})")
        plan.append(f"Week {week_num}: " + " | ".join(items))
    return plan


def build_report(target, score, found, missing, top_roles, roadmap) -> str:
    """Generate a clean, professional plain text analysis report."""
    border = "=" * 65
    sub_border = "-" * 65
    
    lines = [
        border,
        "   AI RESUME ANALYZER & JOB RECOMMENDATION SYSTEM",
        "             COMPREHENSIVE CANDIDATE REPORT",
        border,
        f"Generated Date : {date.today().strftime('%B %d, %Y')}",
        f"Target Role    : {target}",
        f"Match Score    : {score:.1f}%",
        f"Match Formula  : 70% Skill Coverage + 30% TF-IDF Cosine Similarity",
        sub_border,
        "",
        "1. DETECTED SKILLS FROM RESUME:",
        *( [f"   * {s}" for s in found] if found else ["   * No recognizable skills detected from the dictionary."] ),
        f"   Total Skills Detected: {len(found)}",
        "",
        "2. SKILL GAP ANALYSIS FOR TARGET ROLE:",
        f"   Required Skills Missing ({len(missing)}):",
        *( [f"   * [MISSING] {s}" for s in missing] if missing else ["   * None - You possess all listed required skills!"] ),
        "",
        "3. TOP RECOMMENDED JOB ROLES:",
        *[f"   {i}. {r:<28} | Overall Score: {s:.1f}%" for i, (r, s) in enumerate(top_roles, 1)],
        "",
        "4. CUSTOMIZED WEEKLY LEARNING ROADMAP:",
        *[f"   * {w}" for w in roadmap],
        "",
        border,
        "RESPONSIBLE AI & ACADEMIC GUIDANCE DISCLAIMER:",
        "This system uses controlled skill extraction and TF-IDF text similarity",
        "for educational career guidance and skill development.",
        "Scores are advisory estimates and do NOT constitute actual hiring,",
        "screening, or rejection decisions. Protected personal attributes",
        "(gender, age, race, contact details) are strictly excluded from scoring.",
        border,
    ]
    return "\n".join(lines)


def build_markdown_report(target, score, found, missing, top_roles, roadmap) -> str:
    """Generate a modern GitHub Flavored Markdown report."""
    md_lines = [
        "# 📄 AI Resume Analyzer & Job Recommendation Report",
        f"**Generated on:** {date.today().strftime('%B %d, %Y')}  ",
        f"**Target Role:** `{target}`  ",
        f"**Overall Match Score:** `{score:.1f}%`  ",
        "",
        "> **Note:** Scores are algorithmic guidance estimates based on 70% Skill Coverage and 30% TF-IDF Semantic Similarity. This is an educational tool, not an automated hiring gate.",
        "",
        "## 🧩 1. Skills Detected in Resume",
        f"Total skills identified: **{len(found)}**",
        "",
        ", ".join(f"`{s}`" for s in found) if found else "*No matching skills detected.*",
        "",
        "## 🎯 2. Skill Gap Analysis",
        f"### Target Role: {target}",
        "",
        f"- **Missing Skills ({len(missing)}):** " + (", ".join(f"`{s}`" for s in missing) if missing else "None! Complete coverage."),
        "",
        "## 🏆 3. Top Recommended Roles",
        "| Rank | Recommended Role | Match Score |",
        "| :---: | :--- | :---: |",
        *[f"| {i} | **{r}** | {s:.1f}% |" for i, (r, s) in enumerate(top_roles, 1)],
        "",
        "## 🗺️ 4. Tailored Weekly Learning Roadmap",
        *[f"- **{w.split(':', 1)[0]}:** {w.split(':', 1)[1].strip()}" if ":" in w else f"- {w}" for w in roadmap],
        "",
        "---",
        "*Project: AI Resume Analyzer & Job Recommendation System | Major College Project*",
    ]
    return "\n".join(md_lines)


def build_json_report(target, score, found, missing, top_roles, roadmap) -> str:
    """Generate structured JSON report for programmatic consumption."""
    data = {
        "metadata": {
            "system": "AI Resume Analyzer & Job Recommendation System",
            "report_date": str(date.today()),
            "scoring_formula": "70% Skill Coverage + 30% TF-IDF Cosine Similarity",
        },
        "target_role": target,
        "match_score": score,
        "skills_detected": found,
        "skills_detected_count": len(found),
        "missing_skills": missing,
        "missing_skills_count": len(missing),
        "top_recommendations": [{"rank": i, "role": r, "score": s} for i, (r, s) in enumerate(top_roles, 1)],
        "learning_roadmap": roadmap,
    }
    return json.dumps(data, indent=2)

