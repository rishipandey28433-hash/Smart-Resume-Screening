import io
import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def sanitize_csv_cell(value):
    """
    Sanitize text to prevent CSV/formula injection attacks in Excel/Google Sheets.
    If the field begins with =, +, -, @, or tab/carriage return, prepend a single quote.
    """
    if value is None:
        return ""
    val_str = str(value).strip()
    if val_str and val_str[0] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + val_str
    return val_str

def generate_csv_report(job, candidates):
    """
    Generate CSV string with candidate ranking, scores, and status.
    Protected against CSV injection.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Metadata headers
    writer.writerow([sanitize_csv_cell("HireSense AI — Screening Report")])
    writer.writerow([sanitize_csv_cell(f"Job Title: {job['title'] if job else 'General Screening'}")])
    writer.writerow([sanitize_csv_cell(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")])
    writer.writerow([sanitize_csv_cell("Scoring Method: 40% Textual Similarity + 40% Required Skills + 10% Preferred Skills + 10% Experience")])
    writer.writerow([])  # Blank line

    # Table headers
    headers = [
        "Rank",
        "Candidate Name",
        "Match Score (%)",
        "Text Similarity (%)",
        "Skill Match (%)",
        "Status",
        "Email",
        "Phone",
        "Matched Skills",
        "Missing Skills",
        "Resume File",
        "Recruiter Notes"
    ]
    writer.writerow([sanitize_csv_cell(h) for h in headers])

    for i, c in enumerate(candidates, start=1):
        row = [
            str(i),
            c.get("name", "Unknown"),
            f"{c.get('score', 0):.1f}%",
            f"{c.get('text_similarity', 0):.1f}%",
            f"{c.get('skill_score', 0):.1f}%",
            c.get("status", "New"),
            c.get("email", ""),
            c.get("phone", ""),
            c.get("matched_skills", ""),
            c.get("missing_skills", ""),
            c.get("filename", ""),
            c.get("notes", "")
        ]
        writer.writerow([sanitize_csv_cell(field) for field in row])

    return output.getvalue()

def generate_pdf_report(candidate, job=None):
    """
    Generate a professional single-candidate evaluation PDF report using ReportLab.
    Returns a bytes buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        fontName='Helvetica'
    )
    heading_style = ParagraphStyle(
        'SectionHead',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1E3A8A'),
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        fontName='Helvetica'
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#94A3B8'),
        fontName='Helvetica-Oblique'
    )

    elements = []

    # Header / Branding
    elements.append(Paragraph("HireSense AI — Candidate Screening Assessment", title_style))
    elements.append(Paragraph("Smarter Screening. Better Hiring. | Confidential Recruiter Report", subtitle_style))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=15))

    # Candidate & Job Details Table
    job_title = job["title"] if job else "General Technical Screening"
    candidate_name = candidate.get("name", "Candidate")
    email = candidate.get("email") or "Not provided"
    phone = candidate.get("phone") or "Not provided"
    status = candidate.get("status", "New")
    date_str = candidate.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M")

    cand_table_data = [
        [Paragraph("<b>Candidate Name:</b>", body_style), Paragraph(candidate_name, body_style),
         Paragraph("<b>Target Role:</b>", body_style), Paragraph(job_title, body_style)],
        [Paragraph("<b>Email:</b>", body_style), Paragraph(email, body_style),
         Paragraph("<b>Phone:</b>", body_style), Paragraph(phone, body_style)],
        [Paragraph("<b>Evaluation Status:</b>", body_style), Paragraph(f"<b>{status}</b>", body_style),
         Paragraph("<b>Screened Date:</b>", body_style), Paragraph(str(date_str), body_style)],
        [Paragraph("<b>Resume File:</b>", body_style), Paragraph(candidate.get("filename", "N/A"), body_style),
         Paragraph("<b>Assessment ID:</b>", body_style), Paragraph(f"HS-{candidate.get('id', '001')}", body_style)]
    ]
    t = Table(cand_table_data, colWidths=[110, 160, 100, 160])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 14))

    # Match Scores Summary Box
    elements.append(Paragraph("Overall Job-Relevance Scoring", heading_style))
    overall_score = candidate.get("score", 0.0)
    text_sim = candidate.get("text_similarity", 0.0)
    skill_score = candidate.get("skill_score", 0.0)
    recommendation = candidate.get("recommendation", "Evaluation Complete")

    score_table_data = [
        [
            Paragraph("<b>Overall Match Score</b>", body_style),
            Paragraph("<b>Textual Similarity</b>", body_style),
            Paragraph("<b>Required Skills Coverage</b>", body_style),
            Paragraph("<b>Classification</b>", body_style)
        ],
        [
            Paragraph(f"<font size=16 color='#2563EB'><b>{overall_score:.1f}%</b></font>", body_style),
            Paragraph(f"<font size=13><b>{text_sim:.1f}%</b></font>", body_style),
            Paragraph(f"<font size=13><b>{skill_score:.1f}%</b></font>", body_style),
            Paragraph(f"<font size=11 color='#0F172A'><b>{recommendation}</b></font>", body_style)
        ]
    ]
    st = Table(score_table_data, colWidths=[130, 130, 140, 130])
    st.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EFF6FF')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FFFFFF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3B82F6')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DBEAFE')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(st)
    elements.append(Spacer(1, 14))

    # Skills Breakdown Table
    elements.append(Paragraph("Skills Analysis", heading_style))
    matched_skills = candidate.get("matched_skills") or "None identified"
    missing_skills = candidate.get("missing_skills") or "None missing"
    
    skills_data = [
        [Paragraph("<b>Category</b>", body_style), Paragraph("<b>Skills Identified</b>", body_style)],
        [Paragraph("<font color='#16A34A'><b>Matched Required Skills</b></font>", body_style), Paragraph(matched_skills, body_style)],
        [Paragraph("<font color='#DC2626'><b>Missing Required Skills</b></font>", body_style), Paragraph(missing_skills, body_style)]
    ]
    skt = Table(skills_data, colWidths=[150, 380])
    skt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(skt)
    elements.append(Spacer(1, 14))

    # Recruiter Notes if any
    notes = candidate.get("notes")
    if notes:
        elements.append(Paragraph("Recruiter Notes", heading_style))
        elements.append(Paragraph(notes, body_style))
        elements.append(Spacer(1, 14))

    # Methodology & Responsible AI Notice
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=10))
    elements.append(Paragraph(
        "<b>Scoring Methodology:</b> Composite score is calculated based on: 40% Textual Similarity (TF-IDF Cosine Similarity), "
        "40% Required Skills Coverage, 10% Preferred Skills Bonus, and 10% Experience Alignment.",
        disclaimer_style
    ))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        "<b>Ethical & Responsible AI Notice:</b> This report is generated as an algorithmic screening aid to assist human recruiters. "
        "It evaluates objective job-related criteria only and does not infer or utilize protected attributes (age, gender, ethnicity, disability). "
        "All hiring decisions must be finalized through human recruiter judgment and interview evaluations.",
        disclaimer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
