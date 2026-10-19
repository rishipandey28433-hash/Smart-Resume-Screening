import os
from database import get_db_connection

DEMO_JOB = {
    "title": "Full Stack Python & AI Engineer",
    "department": "Engineering",
    "description": (
        "We are looking for a skilled Full Stack Python & AI Engineer to build scalable web applications "
        "and intelligent screening platforms. You will work with Python, Flask, React, and SQL databases. "
        "Experience with REST APIs, Git version control, and containerization with Docker is highly valued. "
        "Familiarity with cloud platforms (AWS), Machine Learning, and Scikit-Learn is a strong plus."
    ),
    "required_skills": "Python, Flask, React, SQL, Git, REST API",
    "preferred_skills": "Docker, AWS, Scikit-Learn, Machine Learning",
    "min_experience": "2+ years",
    "qualification": "Bachelor's in Computer Science or related field",
    "status": "Active"
}

DEMO_CANDIDATES = [
    {
        "name": "Aarav Sharma",
        "email": "aarav.sharma@example.com",
        "phone": "+91 98765 43210",
        "github": "https://github.com/aarav-sharma-dev",
        "linkedin": "https://linkedin.com/in/aarav-sharma-ai",
        "filename": "Aarav_Sharma_Resume.pdf",
        "raw_text": (
            "Aarav Sharma - Full Stack Software Developer\n"
            "Email: aarav.sharma@example.com | Phone: +91 98765 43210 | GitHub: https://github.com/aarav-sharma-dev\n"
            "Summary: 3+ years experience designing web services and AI-driven platforms.\n"
            "Technical Skills: Python, Flask, React, JavaScript, SQL, PostgreSQL, REST API, Git, GitHub, Docker, Scikit-Learn, Machine Learning.\n"
            "Experience: Built microservices using Flask and React; deployed ML pipelines with Scikit-Learn on AWS.\n"
            "Education: B.Tech in Computer Science and Engineering."
        ),
        "score": 91.5,
        "text_similarity": 84.0,
        "skill_score": 100.0,
        "matched_skills": "Python, Flask, React, SQL, Git, REST API",
        "missing_skills": "",
        "matched_preferred": "Docker, Scikit-Learn, Machine Learning",
        "status": "Shortlisted",
        "notes": "Strong candidate with full tech stack coverage and Docker experience. Ready for technical interview.",
        "recommendation": "High Alignment",
        "is_demo": 1
    },
    {
        "name": "Priya Patel",
        "email": "priya.patel@example.com",
        "phone": "+91 91234 56789",
        "github": "https://github.com/priyapatel-code",
        "linkedin": "https://linkedin.com/in/priya-patel",
        "filename": "Priya_Patel_CV.pdf",
        "raw_text": (
            "Priya Patel\n"
            "Frontend & Python Developer\n"
            "Email: priya.patel@example.com | Phone: +91 91234 56789\n"
            "Skills: Python, React, JavaScript, HTML, CSS, SQL, Git, GitHub, REST API.\n"
            "Experience: 2 years building client-facing dashboards and integrating backend REST endpoints.\n"
            "Education: Bachelor of Technology (CSE)."
        ),
        "score": 76.2,
        "text_similarity": 68.5,
        "skill_score": 83.3,
        "matched_skills": "Python, React, SQL, Git, REST API",
        "missing_skills": "Flask",
        "matched_preferred": "",
        "status": "Under Review",
        "notes": "Solid frontend skills and Python knowledge; lacks direct Flask and Docker experience.",
        "recommendation": "Moderate Alignment",
        "is_demo": 1
    },
    {
        "name": "Vikram Malhotra",
        "email": "vikram.m@example.com",
        "phone": "+91 99887 76655",
        "github": "https://github.com/vikram-data",
        "linkedin": "https://linkedin.com/in/vikram-malhotra",
        "filename": "Vikram_Malhotra_Resume.pdf",
        "raw_text": (
            "Vikram Malhotra - Data & AI Enthusiast\n"
            "Email: vikram.m@example.com | Phone: +91 99887 76655\n"
            "Summary: Data Analyst with experience in Python, Pandas, NumPy, Machine Learning, SQL, and Data Analysis.\n"
            "Familiar with Git and exploratory data analysis.\n"
            "Education: B.Sc in Information Technology."
        ),
        "score": 53.8,
        "text_similarity": 58.0,
        "skill_score": 50.0,
        "matched_skills": "Python, SQL, Git",
        "missing_skills": "Flask, React, REST API",
        "matched_preferred": "Machine Learning",
        "status": "Under Review",
        "notes": "Strong data background, but minimal web/frontend experience for full-stack role.",
        "recommendation": "Partial Alignment",
        "is_demo": 1
    },
    {
        "name": "Rohan Deshmukh",
        "email": "rohan.d@example.com",
        "phone": "+91 94455 66778",
        "github": "",
        "linkedin": "",
        "filename": "Rohan_Deshmukh_Profile.pdf",
        "raw_text": (
            "Rohan Deshmukh - Java Developer\n"
            "Email: rohan.d@example.com | Phone: +91 94455 66778\n"
            "Summary: Enterprise backend development with Java, Spring Boot, MySQL, and Hibernate.\n"
            "Experience: 3 years building corporate enterprise services.\n"
            "Education: Master of Computer Applications (MCA)."
        ),
        "score": 32.4,
        "text_similarity": 28.5,
        "skill_score": 16.7,
        "matched_skills": "SQL",
        "missing_skills": "Python, Flask, React, Git, REST API",
        "matched_preferred": "",
        "status": "Rejected",
        "notes": "Enterprise Java specialist; stack mismatch for Python/React role.",
        "recommendation": "Low Textual Match",
        "is_demo": 1
    }
]

def seed_demo_data():
    """Seed synthetic demonstration job and candidate records."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if demo job already exists
    cursor.execute("SELECT id FROM jobs WHERE title = ? AND department = 'Engineering'", (DEMO_JOB["title"],))
    row = cursor.fetchone()
    
    if row:
        job_id = row["id"]
    else:
        cursor.execute("""
            INSERT INTO jobs (title, department, description, required_skills, preferred_skills, min_experience, qualification, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            DEMO_JOB["title"],
            DEMO_JOB["department"],
            DEMO_JOB["description"],
            DEMO_JOB["required_skills"],
            DEMO_JOB["preferred_skills"],
            DEMO_JOB["min_experience"],
            DEMO_JOB["qualification"],
            DEMO_JOB["status"]
        ))
        job_id = cursor.lastrowid

    # Check if demo candidates already exist for this job
    cursor.execute("SELECT COUNT(*) as cnt FROM candidates WHERE job_id = ? AND is_demo = 1", (job_id,))
    existing_cnt = cursor.fetchone()["cnt"]

    if existing_cnt == 0:
        for cand in DEMO_CANDIDATES:
            cursor.execute("""
                INSERT INTO candidates (
                    job_id, name, email, phone, github, linkedin, filename,
                    raw_text, score, text_similarity, skill_score, matched_skills,
                    missing_skills, matched_preferred, status, notes, recommendation, is_demo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id,
                cand["name"],
                cand["email"],
                cand["phone"],
                cand["github"],
                cand["linkedin"],
                cand["filename"],
                cand["raw_text"],
                cand["score"],
                cand["text_similarity"],
                cand["skill_score"],
                cand["matched_skills"],
                cand["missing_skills"],
                cand["matched_preferred"],
                cand["status"],
                cand["notes"],
                cand["recommendation"],
                cand["is_demo"]
            ))

    conn.commit()
    conn.close()
    return job_id

def clear_demo_data():
    """Remove ONLY synthetic/demo data (where is_demo = 1), preserving real records."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete demo candidates
    cursor.execute("DELETE FROM candidates WHERE is_demo = 1")
    demo_cand_deleted = cursor.rowcount

    # Delete demo job if it has no real candidates
    cursor.execute("SELECT id FROM jobs WHERE title = ?", (DEMO_JOB["title"],))
    demo_jobs = cursor.fetchall()
    for dj in demo_jobs:
        cursor.execute("SELECT COUNT(*) as cnt FROM candidates WHERE job_id = ?", (dj["id"],))
        if cursor.fetchone()["cnt"] == 0:
            cursor.execute("DELETE FROM jobs WHERE id = ?", (dj["id"],))

    conn.commit()
    conn.close()
    return demo_cand_deleted
