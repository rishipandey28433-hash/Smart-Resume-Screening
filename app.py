from flask import send_file 
from reportlab.pdfgen import canvas
from flask import Flask, render_template, request
import os
import sqlite3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.parser import extract_text
from utils.skills import extract_skills

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    resume = request.files["resume"]
    job_description = request.form["job_description"]

    if resume.filename == "":
        return "Please Select Resume"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        resume.filename
    )

    resume.save(filepath)

    resume_text = extract_text(filepath)

    documents = [
        resume_text,
        job_description
    ]

    vectorizer = TfidfVectorizer()

    tfidf = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf[0:1],
        tfidf[1:2]
    )

    score = round(
        similarity[0][0] * 100,
        2
    )

    resume_skills = extract_skills(
        resume_text
    )

    jd_skills = extract_skills(
        job_description
    )

    matched_skills = []

    for skill in resume_skills:
        if skill in jd_skills:
            matched_skills.append(skill)

    missing_skills = []

    for skill in jd_skills:
        if skill not in resume_skills:
            missing_skills.append(skill)
            # Recommendation

    if score >= 80:
        recommendation = "Excellent Match"
        color = "#198754"

    elif score >= 60:
        recommendation = "Good Match"
        color = "#fd7e14"

    elif score >= 40:
        recommendation = "Average Match"
        color = "#ffc107"

    else:
        recommendation = "Needs Improvement"
        color = "#dc3545"
        suggestions = []

    if score < 80:
        suggestions.append("Add more relevant technical skills.")

    if "github" not in resume_text.lower():
        suggestions.append("Add your GitHub profile link.")

    if "project" not in resume_text.lower():
        suggestions.append("Include academic or personal projects.")

    if "internship" not in resume_text.lower():
        suggestions.append("Mention internship or practical experience.")

    if len(missing_skills) > 0:
        suggestions.append(
            "Learn these skills: " + ", ".join(missing_skills[:5])
        )

    # Save Result To Database

    conn = sqlite3.connect("resume.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO resumes
        (filename, score, recommendation)
        VALUES (?, ?, ?)
        """,
        (
            resume.filename,
            score,
            recommendation
        )
    )

    conn.commit()
    conn.close()
    return render_template(

        "result.html",

        filename=resume.filename,

        score=score,

        recommendation=recommendation,

        color=color,

        resume_text=resume_text,

        job_description=job_description,

        resume_skills=resume_skills,

        jd_skills=jd_skills,

        matched_skills=matched_skills,

        missing_skills=missing_skills,
        suggestions=suggestions

    )
@app.route("/history")
def history():

    conn = sqlite3.connect("resume.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT filename, score, recommendation
        FROM resumes
        ORDER BY id DESC
    """)

    resumes = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        resumes=resumes
    )
@app.route("/download")
def download_report():

    pdf_file = "Resume_Report.pdf"

    c = canvas.Canvas(pdf_file)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(150, 800, "AI Resume Analysis Report")

    c.setFont("Helvetica", 13)
    c.drawString(50, 760, "Created By: Rishi Pandey")

    c.drawString(50, 730, "Thank you for using AI Resume Screening System.")

    c.save()

    return send_file(pdf_file, as_attachment=True)



if __name__ == "__main__":
    app.run(debug=True)