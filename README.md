# HireSense AI — AI-Powered Resume Screening and Candidate Ranking Platform

> **Tagline:** *Smarter Screening. Better Hiring.*  
> **Application Title:** HireSense AI — Resume Screening & Candidate Ranking  
> **Author:** Rishi Pandey  
> **GitHub Repository:** [HireSense-AI](https://github.com/rishipandey28433-hash/HireSense-AI)

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/Flask-3.1-black?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3+-F7931E?style=flat&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![ReportLab](https://img.shields.io/badge/ReportLab-4.0+-0F172A?style=flat)](https://www.reportlab.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Product Overview

**HireSense AI** is a recruitment-tech software platform built to transform how engineering teams, high-growth startups, and talent acquisition specialists screen and rank candidate resumes. 

Instead of forcing recruiters to spend 15–20 hours per requisition manually reviewing hundreds of PDF or Word documents, HireSense AI provides an intelligent, automated screening pipeline. By combining boundary-safe technical skill extraction with contextual TF-IDF vectorization and cosine similarity, HireSense AI calculates transparent, job-relevance match scores and ranks candidates from highest to lowest alignment.

---

## 2. Problem Statement

Modern technical hiring is constrained by significant operational hurdles:
- **Application Overload:** Postings for software engineering roles routinely attract 200–500+ applications within days.
- **Reviewer Fatigue:** Hiring managers spend an average of only 6–8 seconds per resume, leading to inconsistent and error-prone decisions.
- **Flawed Legacy Keyword Filtering:** Traditional ATS software relies on naive substring searches. For example, looking for the programming language `"C"` mistakenly matches every word containing the letter 'c' (such as "academic", "education", or "experience").
- **The "Black-Box" Dilemma:** Proprietary screening algorithms often output an opaque number without showing recruiters *which* skills were matched and *what* requirements are missing.

---

## 3. Proposed Solution

HireSense AI solves these challenges with an **explainable, human-in-the-loop screening copilot**:
1. **Multi-Format Ingestion:** Robust text extraction across PDF (`pdfplumber`), Microsoft Word DOCX (`python-docx`), and plain text (`.txt`).
2. **Boundary-Safe NLP Extraction:** Curated dictionary of 50+ canonical technical skills using boundary-safe regular expressions (`\b`, negative lookaheads) and synonym normalization (e.g., `React.js` $\rightarrow$ `React`, `Postgres` $\rightarrow$ `PostgreSQL`).
3. **Transparent Hybrid Scoring Engine:** A 4-part composite score combining contextual semantic similarity, mandatory skill coverage, preferred skill bonuses, and experience alignment.
4. **Recruiter Decision Pipeline:** Real-time dashboard with search, filtering, status management (`Shortlisted`, `Under Review`, `Rejected`), interview notes, and one-click exports (sanitized CSV and styled PDF).
5. **Responsible AI Design:** Screening criteria are restricted to objective, job-relevant qualifications. No protected characteristics (age, gender, ethnicity, disability) are extracted or factored into scoring.

---

## 4. Key Implemented Features

- **Recruiter Operations Dashboard:** Real-time metrics calculated directly from database records (Total Jobs, Resumes Processed, Shortlisted Candidates, Average Match Score).
- **Multi-Resume Batch Screening:** Upload multiple PDF, DOCX, and TXT resumes simultaneously against any job requisition.
- **Explainable Ranking Table:** Sortable and filterable candidate leaderboards with score badges, skill pills, and instant status updates.
- **Candidate Assessment Modal:** In-depth evaluation view showing score components, matched skills, missing skills, candidate contact info, and extracted resume excerpts.
- **Confidential Recruiter Notes:** Save interview notes and observations directly onto candidate records.
- **Formula-Safe CSV Export:** Download ranking tables protected against spreadsheet formula injection attacks (`=`, `+`, `-`, `@` escaping).
- **Executive PDF Assessment Reports:** Generate dynamic single-candidate evaluation reports using ReportLab.
- **Synthetic Demo Data Suite:** One-click seeding of sample job requisitions and candidate profiles for instant evaluation, with clean removal controls that never touch genuine user data.
- **Lightweight Recruiter Authentication:** Session-based authentication with secure password hashing (`werkzeug.security`) and an evaluation Guest Recruiter mode.

---

## 5. Technology Stack & Architecture

```
HireSense-AI/
│── app.py                   # Main Flask application and REST routes
│── database.py              # SQLite schema initialization and migration
│── requirements.txt         # Core dependencies
│── resume.db                # SQLite database
│── .env.example             # Safe environment variable configuration template
│── STARTUP_PRESENTATION.md  # Comprehensive venture presentation documentation
│── uploads/                 # Local directory for uploaded candidate documents
│── static/
│   └── css/style.css        # Professional recruitment-tech CSS design system
│── templates/
│   ├── base.html            # Core layout with navigation and footer
│   ├── dashboard.html       # Recruiter analytics dashboard
│   ├── screen.html          # New screening session form & dropzone
│   ├── results.html         # Candidate ranking table & explainability modal
│   ├── jobs.html            # Requisitions management list
│   ├── pricing.html         # Proposed startup pricing tiers
│   ├── about.html           # Value proposition and Responsible AI charter
│   ├── settings.html        # System health and demo data controls
│   ├── login.html           # Recruiter sign-in with 1-click Guest bypass
│   ├── register.html        # Recruiter registration
│   ├── result.html          # Preserved single evaluation view
│   ├── history.html         # Preserved historical activity log
│   ├── 404.html             # Not found error view
│   └── 500.html             # Internal server error view
│── utils/
│   ├── parser.py            # PDF, DOCX, TXT parser & contact heuristic extractor
│   ├── skills.py            # Boundary-safe skill taxonomy & comparison engine
│   ├── scorer.py            # Transparent 4-factor hybrid scoring model
│   ├── reporter.py          # Formula-safe CSV export & ReportLab PDF generator
│   └── demo_data.py         # Synthetic demo data seeder and cleaner
└── tests/
    └── test_hiresense.py    # Automated test suite (13 unit tests)
```

- **Backend:** Python 3.11, Flask 3.1
- **Machine Learning & NLP:** Scikit-Learn (TF-IDF Vectorizer, Cosine Similarity), NumPy
- **Document Processing:** `pdfplumber`, `pypdfium2`, `python-docx`
- **PDF Generation:** `reportlab`
- **Database:** SQLite 3
- **Security:** Werkzeug PBKDF2 Password Hashing, Safe CSV Sanitization

---

## 6. How the Ranking Score is Calculated

HireSense AI utilizes a documented **4-Factor Composite Scoring Model** designed to prevent score inflation and provide explainable ranking:

$$\text{Composite Match Score} = (0.40 \times S_{\text{text}}) + (0.40 \times S_{\text{req}}) + (0.10 \times S_{\text{pref}}) + (0.10 \times S_{\text{exp}})$$

1. **Contextual Text Similarity ($S_{\text{text}}$, 40%):** Measures semantic and vocabulary overlap between the entire resume body and the job description using Scikit-Learn's `TfidfVectorizer(ngram_range=(1,2), stop_words='english')` and Cosine Similarity.
2. **Mandatory Skills Coverage ($S_{\text{req}}$, 40%):** Ratio of required technical skills present in the candidate resume:
   $$S_{\text{req}} = \frac{\text{Count of Matched Required Skills}}{\text{Total Required Skills Defined}}$$
3. **Preferred Skills Bonus ($S_{\text{pref}}$, 10%):** Rewards candidates who possess optional "nice-to-have" skills (e.g., Docker, AWS, Scikit-Learn).
4. **Experience & Domain Alignment ($S_{\text{exp}}$, 10%):** Heuristic evaluation comparing candidate experience duration against the requisition requirement.

### Match Alignment Tiers:
- **$\ge 80.0\%$ — High Alignment:** Strong skill coverage and deep contextual match.
- **$60.0\% - 79.9\%$ — Moderate Alignment:** Core competencies met with few missing secondary requirements.
- **$40.0\% - 59.9\%$ — Partial Alignment:** Foundational overlap with noticeable skill gaps.
- **$< 40.0\%$ — Low Textual Match:** Limited overlap; manual recruiter review advised.

---

## 7. Installation and Local Run Instructions (Windows PowerShell)

### Prerequisites:
- Python 3.10+ (Verified on Python 3.11)
- Git

### Step-by-Step Commands:

```powershell
# 1. Clone repository
git clone https://github.com/rishipandey28433-hash/HireSense-AI.git
cd HireSense-AI

# 2. (Optional but recommended) Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Initialize database schema
python database.py

# 5. Run automated test suite to verify installation
python -m unittest tests/test_hiresense.py -v

# 6. Launch HireSense AI application
python app.py
```

Open your web browser and navigate to:  
👉 **`http://127.0.0.1:5000`**

---

## 8. Environment Variable Configuration

Create a local `.env` file from the provided template:

```powershell
Copy-Item .env.example .env
```

Configurable variables in `.env`:
```ini
SECRET_KEY=your-secure-secret-key-for-flask-sessions
FLASK_ENV=development
DATABASE_PATH=resume.db
PORT=5000
```

---

## 9. Database Setup & Migrations

The platform uses SQLite 3 (`resume.db`). To initialize or upgrade the database:

```powershell
python database.py
```

The database initialization script is idempotent: it preserves all existing `resumes` records while creating `users`, `jobs`, and `candidates` tables along with optimized performance indexes (`idx_candidates_job_id`, `idx_candidates_score`).

---

## 10. Testing Instructions

HireSense AI includes an automated unit test suite covering document parsing, regex boundaries, scoring, CSV security, and HTTP routes.

Run the test suite with verbose output:

```powershell
python -m unittest tests/test_hiresense.py -v
```

Expected test results:
```
test_compare_skills ... ok
test_contact_info_extraction ... ok
test_csv_injection_sanitization ... ok
test_demo_data_cycle ... ok
test_docx_extraction ... ok
test_empty_and_corrupt_files ... ok
test_evaluate_candidate ... ok
test_pdf_report_generation ... ok
test_recruiter_screening_flow ... ok
test_routes_status_codes ... ok
test_skill_synonyms ... ok
test_txt_extraction ... ok
test_word_boundary_safety ... ok

Ran 13 tests in 0.788s
OK
```

---

## 11. Deployment Instructions

### Production Deployment with Gunicorn (Linux / Container):
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

### Production Checklist:
1. Set `FLASK_ENV=production` and generate a cryptographically secure `SECRET_KEY`.
2. Configure a reverse proxy (e.g., NGINX or Caddy) with SSL/TLS encryption.
3. Enable HTTPS secure cookie flags:
   ```python
   app.config['SESSION_COOKIE_SECURE'] = True
   app.config['SESSION_COOKIE_HTTPONLY'] = True
   ```
4. Configure persistent volume mounts for `uploads/` and `resume.db`.

---

## 12. Security and Privacy

- **Spreadsheet Formula Injection Protection:** Exported CSV cells beginning with `=`, `+`, `-`, or `@` are safely prepended with `'` to prevent remote command execution in Microsoft Excel.
- **Upload Sanitization:** All uploaded files are sanitized via `werkzeug.utils.secure_filename` with random hex tokens to block path traversal (`../../`).
- **Cryptographic Password Storage:** Passwords are never stored in plaintext; credentials use PBKDF2 with SHA-256 password hashing.
- **Candidate Privacy:** Uploaded documents are stored locally for recruiter review and are never transmitted to external third-party advertisers.

---

## 13. Current Limitations & Future Roadmap

### Current Prototype Limitations:
- Scanned image-only PDFs without an embedded text layer cannot be parsed without an OCR engine.
- Synonym mapping relies on an extensive taxonomy (50+ skills) rather than dense vector embeddings.

### Future Enhancements Roadmap:
1. **Tesseract OCR Integration:** Optical Character Recognition for scanned physical resumes.
2. **Dense Vector Embeddings:** Sentence-Transformers (SBERT / MiniLM) for semantic phrase matching.
3. **ATS Bi-directional Webhooks:** Live integrations with Greenhouse, Lever, and Workable.
4. **Applicant Feedback Portal:** Allow candidates to preview resume alignment before submitting.

---

## 14. Proposed Commercial Model

*Note: Proposed model for startup presentation evaluation.*

- **Free Trial:** 14-day trial, 25 resumes/batch, basic PDF reports.
- **Starter (₹2,499 / Month):** 500 resumes/month, unlimited job pipelines, full explainability dashboard, 3 recruiter seats.
- **Business (₹6,999 / Month):** Unlimited resume screening, 10 recruiter seats, priority processing queue, branded PDF reports.

---

## Author & Academic Attribution

**Developer:** Rishi Pandey  
**Project:** B.Tech CSE Startup & Entrepreneurial Activity Evaluation  
**Presentation Guide:** See [STARTUP_PRESENTATION.md](STARTUP_PRESENTATION.md) for full pitch deck notes, evaluation demo walkthrough, and Q&A preparation.
