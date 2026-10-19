import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.skills import extract_skills, compare_skills

def calculate_text_similarity(resume_text, job_description):
    """
    Compute cosine similarity between resume text and job description using TF-IDF.
    Returns: float between 0.0 and 1.0
    """
    if not resume_text or not job_description:
        return 0.0

    try:
        # Preprocessing: clean excessive whitespace
        clean_resume = " ".join(resume_text.split())
        clean_jd = " ".join(job_description.split())
        
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2)
        )
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(max(0.0, min(1.0, sim)))
    except Exception:
        return 0.0

def evaluate_candidate(resume_text, job_description, required_skills=None, preferred_skills=None, min_experience_text=""):
    """
    Calculate transparent, explainable job-relevance match score and candidate insights.
    
    Weights:
    - 40% Textual Similarity (TF-IDF cosine similarity of full context)
    - 40% Required Skills Coverage (Ratio of required skills matched)
    - 10% Preferred Skills Coverage (Ratio of preferred skills matched)
    - 10% Experience & Role Alignment (Detection of target experience & background)
    
    Returns structured dict with explainability details, recommendations, and disclaimer.
    """
    # 1. Extract skills from resume
    resume_skills = extract_skills(resume_text)
    
    # 2. Determine required skills (auto-extract from JD if not provided)
    if not required_skills:
        required_skills = extract_skills(job_description)
    if preferred_skills is None:
        preferred_skills = []

    # 3. Compare skills
    skill_comparison = compare_skills(resume_skills, required_skills, preferred_skills)
    req_ratio = skill_comparison["required_ratio"]
    pref_ratio = skill_comparison["preferred_ratio"]

    # 4. Compute Textual Similarity
    text_sim = calculate_text_similarity(resume_text, job_description)

    # 5. Experience / Domain Keyword Alignment (0.0 to 1.0)
    exp_alignment = 0.5  # Neutral baseline
    if min_experience_text:
        # Check if experience numbers match
        exp_digits = re.findall(r'\d+', min_experience_text)
        if exp_digits:
            target_yrs = int(exp_digits[0])
            # Search candidate text for years
            cand_exp_matches = re.findall(r'(\d+)\s*\+?\s*(?:years?|yrs?)', resume_text, re.IGNORECASE)
            if cand_exp_matches:
                cand_yrs = max([int(y) for y in cand_exp_matches])
                if cand_yrs >= target_yrs:
                    exp_alignment = 1.0
                elif cand_yrs >= max(1, target_yrs - 1):
                    exp_alignment = 0.75
                else:
                    exp_alignment = 0.4
            else:
                exp_alignment = 0.5
    else:
        # General professional indicators
        exp_alignment = 0.8 if any(k in resume_text.lower() for k in ["experience", "work history", "employment", "internship", "projects"]) else 0.5

    # 6. Hybrid Weighted Scoring
    if required_skills:
        score_val = (
            (text_sim * 0.40) +
            (req_ratio * 0.40) +
            (pref_ratio * 0.10) +
            (exp_alignment * 0.10)
        ) * 100.0
    else:
        # Fallback to pure textual similarity if no required skills identified
        score_val = text_sim * 100.0

    overall_score = round(max(0.0, min(100.0, score_val)), 1)
    text_sim_score = round(text_sim * 100.0, 1)
    skill_score = round(req_ratio * 100.0, 1)

    # 7. Tier & Recommendation (Fair, non-pejorative terminology)
    if overall_score >= 80:
        recommendation = "High Alignment"
        badge_class = "badge-success"
        color = "#10b981"  # Emerald Green
    elif overall_score >= 60:
        recommendation = "Moderate Alignment"
        badge_class = "badge-primary"
        color = "#2563eb"  # Royal Blue
    elif overall_score >= 40:
        recommendation = "Partial Alignment"
        badge_class = "badge-warning"
        color = "#f59e0b"  # Amber
    else:
        recommendation = "Low Textual Match"
        badge_class = "badge-secondary"
        color = "#64748b"  # Slate Gray

    # 8. Actionable Insights & Explainability
    reasons = []
    if required_skills:
        reasons.append(f"Matched {len(skill_comparison['matched_required'])} of {len(required_skills)} required technical skills ({skill_score}%).")
    if skill_comparison["matched_preferred"]:
        reasons.append(f"Matched {len(skill_comparison['matched_preferred'])} preferred skill(s): {', '.join(skill_comparison['matched_preferred'][:3])}.")
    if skill_comparison["missing_required"]:
        reasons.append(f"Key missing skills to verify during interview: {', '.join(skill_comparison['missing_required'][:4])}.")
    reasons.append(f"Contextual text similarity with job description: {text_sim_score}%.")

    # Suggestions for candidate improvement or recruiter inquiry
    suggestions = []
    if skill_comparison["missing_required"]:
        suggestions.append(f"Clarify candidate's familiarity with required stack: {', '.join(skill_comparison['missing_required'][:3])}.")
    if "github" not in resume_text.lower():
        suggestions.append("Candidate resume does not mention code repositories or GitHub links.")
    if "project" not in resume_text.lower():
        suggestions.append("Check portfolio for practical or open-source software projects.")

    return {
        "overall_score": overall_score,
        "text_similarity_score": text_sim_score,
        "skill_score": skill_score,
        "recommendation": recommendation,
        "badge_class": badge_class,
        "color": color,
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "matched_skills": skill_comparison["matched_required"],
        "missing_skills": skill_comparison["missing_required"],
        "matched_preferred": skill_comparison["matched_preferred"],
        "missing_preferred": skill_comparison["missing_preferred"],
        "additional_skills": skill_comparison["additional_skills"],
        "reasons": reasons,
        "suggestions": suggestions,
        "scoring_methodology": (
            "Composite Score = 40% Textual Similarity (TF-IDF Cosine) + "
            "40% Required Skills Coverage + 10% Preferred Skills Bonus + "
            "10% Experience Alignment."
        ),
        "disclaimer": (
            "Responsible AI Notice: This match score is an algorithmic screening aid based solely on "
            "job-related keywords and text similarity. It does not measure candidate character, future performance, "
            "or potential. All screening and hiring decisions must be reviewed and made by a human recruiter."
        )
    }
