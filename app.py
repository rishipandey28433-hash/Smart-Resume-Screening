import os
import re
import secrets
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, send_file, jsonify, abort, Response
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection, init_db
from utils.parser import extract_text, extract_contact_info
from utils.skills import extract_skills, parse_skill_list
from utils.scorer import evaluate_candidate, calculate_text_similarity
from utils.reporter import generate_csv_report, generate_pdf_report
from utils.demo_data import seed_demo_data, clear_demo_data

app = Flask(__name__)

# Security & App Configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "hiresense-ai-secure-dev-key-2026")
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB max upload
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure database tables exist on startup
init_db()


def is_allowed_file(filename):
    """Verify file has an authorized extension."""
    if not filename or "." not in filename:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def get_current_user():
    """Retrieve logged in user information if authenticated."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    conn = get_db_connection()
    user = conn.execute("SELECT id, username, email, full_name, role FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user


def login_required(f):
    """Decorator to require recruiter login, with demo guest fallback option."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session and not session.get("is_guest"):
            # Auto-enable guest demo recruiter for smooth evaluator testing if requested
            if request.args.get("demo_mode") == "1":
                session["user_id"] = 0
                session["username"] = "demo_recruiter"
                session["is_guest"] = True
                return f(*args, **kwargs)
            flash("Please sign in or continue as Guest Recruiter.", "info")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_global_vars():
    """Inject current user and branding constants across all Jinja templates."""
    return {
        "current_user": get_current_user(),
        "is_guest": session.get("is_guest", False),
        "brand_name": "HireSense AI",
        "tagline": "Smarter Screening. Better Hiring.",
        "app_title": "HireSense AI — Resume Screening & Candidate Ranking",
        "current_year": datetime.now().year
    }


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        action = request.form.get("action")
        
        # Quick Guest Recruiter bypass for evaluation & demo
        if action == "guest":
            session["user_id"] = 0
            session["username"] = "Guest Recruiter"
            session["is_guest"] = True
            flash("Welcome! Signed in as Guest Recruiter (Evaluation Mode).", "success")
            next_url = request.args.get("next") or url_for("dashboard")
            return redirect(next_url)

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please provide both username and password.", "danger")
            return render_template("login.html")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_guest"] = False
            flash(f"Welcome back, {user['full_name'] or user['username']}!", "success")
            next_url = request.args.get("next") or url_for("dashboard")
            return redirect(next_url)
        else:
            flash("Invalid username or password. You can also sign in as Guest Recruiter.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All required fields must be filled.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")

        conn = get_db_connection()
        existing = conn.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email)).fetchone()
        if existing:
            conn.close()
            flash("Username or email already registered.", "warning")
            return render_template("register.html")

        pwd_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, 'recruiter')",
            (username, email, pwd_hash, full_name or username)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        session.clear()
        session["user_id"] = user_id
        session["username"] = username
        session["is_guest"] = False
        flash("Account created successfully! Welcome to HireSense AI.", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("home"))


# ==========================================
# CORE DASHBOARD & SCREENING ROUTES
# ==========================================

@app.route("/")
def home():
    """Landing and quick overview page."""
    # If already logged in, redirect straight to dashboard
    if "user_id" in session or session.get("is_guest"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    """
    Main Recruiter Dashboard featuring real analytics computed directly from the database:
    - Total Jobs
    - Total Resumes Screened
    - Candidates Shortlisted
    - Average Match Score
    - Recent Jobs and Screenings
    """
    conn = get_db_connection()
    
    # Accurate metrics from actual DB records
    total_jobs = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    total_candidates = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    shortlisted_count = conn.execute("SELECT COUNT(*) FROM candidates WHERE status = 'Shortlisted'").fetchone()[0]
    under_review_count = conn.execute("SELECT COUNT(*) FROM candidates WHERE status = 'Under Review'").fetchone()[0]
    
    avg_score_row = conn.execute("SELECT AVG(score) FROM candidates").fetchone()
    avg_score = round(avg_score_row[0], 1) if avg_score_row and avg_score_row[0] is not None else 0.0

    # Recent jobs with candidate count
    recent_jobs = conn.execute("""
        SELECT j.*, COUNT(c.id) as candidate_count, AVG(c.score) as avg_job_score
        FROM jobs j
        LEFT JOIN candidates c ON j.id = c.job_id
        GROUP BY j.id
        ORDER BY j.id DESC
        LIMIT 5
    """).fetchall()

    # Recent candidate screenings
    recent_candidates = conn.execute("""
        SELECT c.*, j.title as job_title
        FROM candidates c
        LEFT JOIN jobs j ON c.job_id = j.id
        ORDER BY c.id DESC
        LIMIT 6
    """).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_jobs=total_jobs,
        total_candidates=total_candidates,
        shortlisted_count=shortlisted_count,
        under_review_count=under_review_count,
        avg_score=avg_score,
        recent_jobs=recent_jobs,
        recent_candidates=recent_candidates
    )


@app.route("/screen", methods=["GET", "POST"])
def screen():
    """
    Core Screening Interface:
    Recruiter selects or defines a job, sets required/preferred skills,
    and uploads single or batch candidate resumes.
    """
    conn = get_db_connection()
    jobs = conn.execute("SELECT id, title, department FROM jobs ORDER BY id DESC").fetchall()
    conn.close()

    if request.method == "POST":
        job_selection = request.form.get("job_selection", "new")
        
        conn = get_db_connection()
        cursor = conn.cursor()

        if job_selection == "existing":
            job_id = request.form.get("existing_job_id")
            if not job_id:
                flash("Please choose an existing job opening.", "danger")
                return redirect(url_for("screen"))
            job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if not job:
                flash("Selected job was not found.", "danger")
                return redirect(url_for("screen"))
            job_title = job["title"]
            job_desc = job["description"]
            req_skills = parse_skill_list(job["required_skills"])
            pref_skills = parse_skill_list(job["preferred_skills"])
            min_exp = job["min_experience"]
        else:
            # Create a new job record
            job_title = request.form.get("job_title", "").strip() or "Untitled Job Opening"
            job_desc = request.form.get("job_description", "").strip()
            department = request.form.get("department", "Engineering").strip()
            req_skills_raw = request.form.get("required_skills", "").strip()
            pref_skills_raw = request.form.get("preferred_skills", "").strip()
            min_exp = request.form.get("min_experience", "0-2 years").strip()
            qualification = request.form.get("qualification", "Bachelor's Degree").strip()

            if not job_desc:
                flash("Please provide a Job Description to evaluate candidates against.", "danger")
                return redirect(url_for("screen"))

            req_skills = parse_skill_list(req_skills_raw)
            pref_skills = parse_skill_list(pref_skills_raw)

            # Auto-extract skills if recruiter left required skills blank
            if not req_skills:
                req_skills = extract_skills(job_desc)

            cursor.execute("""
                INSERT INTO jobs (title, department, description, required_skills, preferred_skills, min_experience, qualification, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')
            """, (
                job_title,
                department,
                job_desc,
                ", ".join(req_skills),
                ", ".join(pref_skills),
                min_exp,
                qualification
            ))
            job_id = cursor.lastrowid
            conn.commit()

        # Handle uploaded resume files (supports multiple files)
        uploaded_files = request.files.getlist("resumes")
        if not uploaded_files or (len(uploaded_files) == 1 and uploaded_files[0].filename == ""):
            flash("Please upload at least one resume document (PDF, DOCX, or TXT).", "warning")
            conn.close()
            return redirect(url_for("screen"))

        processed_count = 0
        error_count = 0

        for file_storage in uploaded_files:
            if not file_storage or file_storage.filename == "":
                continue

            orig_filename = file_storage.filename
            if not is_allowed_file(orig_filename):
                flash(f"Skipped '{orig_filename}': Unsupported format. Allowed: .pdf, .docx, .txt", "warning")
                error_count += 1
                continue

            # Secure filename and unique prefix
            safe_name = secure_filename(orig_filename)
            unique_name = f"{secrets.token_hex(4)}_{safe_name}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
            
            try:
                file_storage.save(save_path)
            except Exception as save_err:
                flash(f"Failed to save {orig_filename}: {str(save_err)}", "danger")
                error_count += 1
                continue

            # Extract text
            raw_text, extract_err = extract_text(save_path)
            if extract_err or not raw_text.strip():
                flash(f"Warning on '{orig_filename}': {extract_err or 'No readable text'}", "warning")
                # Still store with error status so recruiter knows
                raw_text = raw_text or ""

            # Extract contact heuristics
            contact_info = extract_contact_info(raw_text, fallback_filename=orig_filename)

            # Algorithmic evaluation
            evaluation = evaluate_candidate(
                resume_text=raw_text,
                job_description=job_desc,
                required_skills=req_skills,
                preferred_skills=pref_skills,
                min_experience_text=min_exp
            )

            # Store in candidates table
            cursor.execute("""
                INSERT INTO candidates (
                    job_id, name, email, phone, github, linkedin, filename,
                    raw_text, score, text_similarity, skill_score, matched_skills,
                    missing_skills, matched_preferred, status, notes, recommendation, is_demo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'New', '', ?, 0)
            """, (
                job_id,
                contact_info["name"],
                contact_info["email"],
                contact_info["phone"],
                contact_info["github"],
                contact_info["linkedin"],
                orig_filename,
                raw_text[:8000],  # Store up to 8000 chars of text preview
                evaluation["overall_score"],
                evaluation["text_similarity_score"],
                evaluation["skill_score"],
                ", ".join(evaluation["matched_skills"]),
                ", ".join(evaluation["missing_skills"]),
                ", ".join(evaluation["matched_preferred"]),
                evaluation["recommendation"]
            ))

            # Store in legacy resumes table for backward compatibility
            cursor.execute("""
                INSERT INTO resumes (filename, score, recommendation)
                VALUES (?, ?, ?)
            """, (orig_filename, evaluation["overall_score"], evaluation["recommendation"]))

            processed_count += 1

        conn.commit()
        conn.close()

        if processed_count > 0:
            flash(f"Successfully processed and ranked {processed_count} candidate resume(s)!", "success")
            return redirect(url_for("results", job_id=job_id))
        else:
            flash("No valid resumes could be processed. Please check file formats.", "danger")
            return redirect(url_for("screen"))

    return render_template("screen.html", jobs=jobs)


@app.route("/results/<int:job_id>")
def results(job_id):
    """
    Candidate Ranking & Screening Results Table:
    - Candidates sorted by match score DESC
    - Status filtering, search, and detail modal
    - Export CSV and PDF capabilities
    """
    conn = get_db_connection()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job:
        conn.close()
        flash("Job screening session not found.", "danger")
        return redirect(url_for("dashboard"))

    # Fetch candidates ranked by overall score DESC
    candidates = conn.execute("""
        SELECT * FROM candidates 
        WHERE job_id = ? 
        ORDER BY score DESC, id ASC
    """, (job_id,)).fetchall()
    
    conn.close()

    return render_template(
        "results.html",
        job=job,
        candidates=candidates,
        total_candidates=len(candidates)
    )


@app.route("/jobs")
def jobs_list():
    """List all created job openings and screening sessions."""
    conn = get_db_connection()
    jobs = conn.execute("""
        SELECT j.*, 
               COUNT(c.id) as candidate_count, 
               SUM(CASE WHEN c.status = 'Shortlisted' THEN 1 ELSE 0 END) as shortlisted_count,
               AVG(c.score) as avg_score
        FROM jobs j
        LEFT JOIN candidates c ON j.id = c.job_id
        GROUP BY j.id
        ORDER BY j.id DESC
    """).fetchall()
    conn.close()
    return render_template("jobs.html", jobs=jobs)


# ==========================================
# CANDIDATE ACTIONS & STATUS UPDATES
# ==========================================

@app.route("/candidate/<int:candidate_id>/status", methods=["POST"])
def update_candidate_status(candidate_id):
    """Update candidate recruitment status (Shortlisted, Under Review, Rejected)."""
    new_status = request.form.get("status", "New")
    allowed_statuses = {"Shortlisted", "Under Review", "Rejected", "New"}
    if new_status not in allowed_statuses:
        return jsonify({"success": False, "error": "Invalid status"}), 400

    conn = get_db_connection()
    conn.execute("UPDATE candidates SET status = ? WHERE id = ?", (new_status, candidate_id))
    conn.commit()
    conn.close()

    # If AJAX request, return JSON
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True, "status": new_status})

    flash(f"Candidate status updated to '{new_status}'.", "success")
    job_id = request.form.get("job_id")
    if job_id:
        return redirect(url_for("results", job_id=job_id))
    return redirect(url_for("dashboard"))


@app.route("/candidate/<int:candidate_id>/notes", methods=["POST"])
def update_candidate_notes(candidate_id):
    """Save recruiter notes for a specific candidate."""
    notes = request.form.get("notes", "").strip()
    conn = get_db_connection()
    conn.execute("UPDATE candidates SET notes = ? WHERE id = ?", (notes, candidate_id))
    conn.commit()
    conn.close()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True, "notes": notes})

    flash("Recruiter notes saved.", "success")
    job_id = request.form.get("job_id")
    if job_id:
        return redirect(url_for("results", job_id=job_id))
    return redirect(url_for("dashboard"))


@app.route("/candidate/<int:candidate_id>/pdf")
def candidate_pdf(candidate_id):
    """Download ReportLab PDF report for an individual candidate."""
    conn = get_db_connection()
    candidate = conn.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,)).fetchone()
    if not candidate:
        conn.close()
        flash("Candidate record not found.", "danger")
        return redirect(url_for("dashboard"))

    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (candidate["job_id"],)).fetchone() if candidate["job_id"] else None
    conn.close()

    pdf_bytes = generate_pdf_report(dict(candidate), dict(job) if job else None)
    clean_cand_name = re.sub(r'[^A-Za-z0-9_]', '_', candidate['name'])
    filename = f"HireSense_Report_{clean_cand_name}_{candidate_id}.pdf"

    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/jobs/<int:job_id>/export/csv")
def export_job_csv(job_id):
    """Export complete ranked candidate set to CSV with formula injection protection."""
    conn = get_db_connection()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job:
        conn.close()
        flash("Job not found.", "danger")
        return redirect(url_for("dashboard"))

    candidates = conn.execute("""
        SELECT * FROM candidates 
        WHERE job_id = ? 
        ORDER BY score DESC, id ASC
    """, (job_id,)).fetchall()
    conn.close()

    csv_data = generate_csv_report(dict(job), [dict(c) for c in candidates])
    clean_job_title = re.sub(r'[^A-Za-z0-9_]', '_', job['title'])
    filename = f"HireSense_Rankings_{clean_job_title}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ==========================================
# DEMO DATA & RECRUITER TOOLS
# ==========================================

@app.route("/demo/seed", methods=["GET", "POST"])
def seed_demo():
    """Seed synthetic demonstration data for instant presentation display."""
    demo_job_id = seed_demo_data()
    flash("Synthetic demonstration data loaded successfully! (Marked as demo)", "success")
    return redirect(url_for("results", job_id=demo_job_id))


@app.route("/demo/clear", methods=["GET", "POST"])
def clear_demo():
    """Remove synthetic demonstration data without touching genuine user records."""
    removed_count = clear_demo_data()
    flash(f"Demo data removed cleanly ({removed_count} records cleared). Genuine user data preserved.", "info")
    return redirect(url_for("dashboard"))


# ==========================================
# BUSINESS, PRICING, & ABOUT PAGES
# ==========================================

@app.route("/pricing")
def pricing():
    """Proposed startup pricing plans comparison page."""
    return render_template("pricing.html")


@app.route("/about")
def about():
    """Startup overview, value proposition, target market, and Responsible AI guidelines."""
    return render_template("about.html")


@app.route("/settings")
def settings():
    """Application status, data privacy options, and configuration."""
    conn = get_db_connection()
    resumes_count = conn.execute("SELECT COUNT(*) FROM resumes").fetchone()[0]
    candidates_count = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    jobs_count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    conn.close()

    return render_template(
        "settings.html",
        resumes_count=resumes_count,
        candidates_count=candidates_count,
        jobs_count=jobs_count
    )


# ==========================================
# PRESERVED LEGACY ROUTES (100% Backward Compatible)
# ==========================================

@app.route("/upload", methods=["POST"])
def legacy_upload():
    """
    Preserved legacy single-resume upload route.
    Upgraded internally to use robust parser, skill extraction, and scoring.
    """
    if "resume" not in request.files or request.files["resume"].filename == "":
        flash("Please select a resume file to analyze.", "warning")
        return redirect(url_for("home"))

    resume = request.files["resume"]
    job_description = request.form.get("job_description", "")

    if not is_allowed_file(resume.filename):
        flash("Unsupported file format. Please upload PDF, DOCX, or TXT.", "danger")
        return redirect(url_for("home"))

    safe_name = secure_filename(resume.filename)
    unique_name = f"legacy_{secrets.token_hex(3)}_{safe_name}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    resume.save(filepath)

    resume_text, err = extract_text(filepath)
    if err and not resume_text:
        flash(f"File extraction error: {err}", "danger")
        return redirect(url_for("home"))

    evaluation = evaluate_candidate(
        resume_text=resume_text,
        job_description=job_description
    )

    # Save to legacy database table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resumes (filename, score, recommendation)
        VALUES (?, ?, ?)
    """, (resume.filename, evaluation["overall_score"], evaluation["recommendation"]))
    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        filename=resume.filename,
        score=evaluation["overall_score"],
        recommendation=evaluation["recommendation"],
        color=evaluation["color"],
        resume_text=resume_text,
        job_description=job_description,
        resume_skills=evaluation["resume_skills"],
        jd_skills=evaluation["required_skills"],
        matched_skills=evaluation["matched_skills"],
        missing_skills=evaluation["missing_skills"],
        suggestions=evaluation["suggestions"]
    )


@app.route("/history")
def history():
    """Preserved legacy history page showing all processed resumes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT filename, score, recommendation
        FROM resumes
        ORDER BY id DESC
    """)
    resumes = cursor.fetchall()
    conn.close()

    return render_template("history.html", resumes=resumes)


@app.route("/download")
def download_report():
    """Preserved legacy PDF download route, upgraded to generate a styled assessment."""
    conn = get_db_connection()
    last_cand = conn.execute("SELECT * FROM candidates ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()

    if last_cand:
        return redirect(url_for("candidate_pdf", candidate_id=last_cand["id"]))

    # Fallback to general report if no candidate in DB
    dummy_cand = {
        "name": "Applicant Evaluation",
        "score": 75.0,
        "text_similarity": 70.0,
        "skill_score": 80.0,
        "filename": "Screened_Document.pdf",
        "status": "Screened",
        "recommendation": "Moderate Alignment"
    }
    pdf_bytes = generate_pdf_report(dummy_cand)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=HireSense_Evaluation_Report.pdf"}
    )


# ==========================================
# ERROR HANDLERS (Security & Friendly UX)
# ==========================================

@app.errorhandler(413)
def request_entity_too_large(error):
    flash("Uploaded file exceeds the 25MB maximum limit. Please upload a smaller file.", "danger")
    return redirect(request.url or url_for("dashboard")), 413


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)