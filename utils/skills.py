import re

# Comprehensive canonical skills dictionary with boundary-safe patterns
SKILL_TAXONOMY = {
    # Programming Languages
    "Python": [r'\bpython\b', r'\bpython3\b'],
    "Java": [r'\bjava\b(?!\s*script)'],
    "C": [r'(?<![a-zA-Z0-9_#+])C(?![a-zA-Z0-9_#+])'],
    "C++": [r'(?<![a-zA-Z0-9_])c\+\+(?![a-zA-Z0-9_+])', r'\bcpp\b'],
    "C#": [r'(?<![a-zA-Z0-9_])c#(?![a-zA-Z0-9_#])', r'\bcsharp\b'],
    "JavaScript": [r'\bjavascript\b', r'\bjs\b', r'\bes6\b'],
    "TypeScript": [r'\btypescript\b', r'\bts\b'],
    "Go": [r'\bgolang\b', r'\bgo\s+language\b'],
    "Rust": [r'\brust\b'],
    "PHP": [r'\bphp\b'],
    "Ruby": [r'\bruby\b', r'\bruby\s+on\s+rails\b', r'\brails\b'],
    "Kotlin": [r'\bkotlin\b'],
    "Swift": [r'\bswift\b'],
    "SQL": [r'\bsql\b', r'\btransact-sql\b', r'\bt-sql\b', r'\bpl\/sql\b'],
    "R": [r'(?<![a-zA-Z0-9_])R(?![a-zA-Z0-9_])\s+(?:programming|language|studio)'],

    # Web & Frontend
    "HTML": [r'\bhtml\b', r'\bhtml5\b'],
    "CSS": [r'\bcss\b', r'\bcss3\b'],
    "React": [r'\breact\b', r'\breact\.?js\b', r'\breactjs\b'],
    "Angular": [r'\bangular\b', r'\bangularjs\b'],
    "Vue.js": [r'\bvue\b', r'\bvue\.?js\b', r'\bvuejs\b'],
    "Next.js": [r'\bnext\.?js\b', r'\bnextjs\b'],
    "Tailwind CSS": [r'\btailwind\b', r'\btailwind\s*css\b'],
    "Bootstrap": [r'\bbootstrap\b'],
    "Redux": [r'\bredux\b'],
    "jQuery": [r'\bjquery\b'],

    # Backend & Frameworks
    "Node.js": [r'\bnode\b', r'\bnode\.?js\b', r'\bnodejs\b'],
    "Express": [r'\bexpress\b', r'\bexpress\.?js\b', r'\bexpressjs\b'],
    "Flask": [r'\bflask\b'],
    "Django": [r'\bdjango\b'],
    "FastAPI": [r'\bfastapi\b'],
    "Spring Boot": [r'\bspring\s*boot\b', r'\bspring\s*framework\b'],
    ".NET": [r'\b\.net\b', r'\bdotnet\b', r'\basp\.net\b'],
    "REST API": [r'\brest\b', r'\brestful\b', r'\brest\s*api\b', r'\bweb\s*apis?\b'],
    "GraphQL": [r'\bgraphql\b'],
    "Microservices": [r'\bmicroservices?\b'],

    # Databases
    "MongoDB": [r'\bmongodb\b', r'\bmongo\b'],
    "PostgreSQL": [r'\bpostgresql\b', r'\bpostgres\b'],
    "MySQL": [r'\bmysql\b'],
    "SQLite": [r'\bsqlite\b', r'\bsqlite3\b'],
    "Redis": [r'\bredis\b'],
    "Oracle Database": [r'\boracle\s*(?:db|database)?\b'],
    "Firebase": [r'\bfirebase\b', r'\bfirestore\b'],

    # Cloud & DevOps
    "AWS": [r'\baws\b', r'\bamazon\s+web\s+services\b'],
    "Docker": [r'\bdocker\b', r'\bcontainerization\b'],
    "Kubernetes": [r'\bkubernetes\b', r'\bk8s\b'],
    "Azure": [r'\bazure\b', r'\bmicrosoft\s+azure\b'],
    "Google Cloud (GCP)": [r'\bgcp\b', r'\bgoogle\s+cloud(?:\s+platform)?\b'],
    "CI/CD": [r'\bci[\/-]cd\b', r'\bcontinuous\s+integration\b', r'\bjenkins\b', r'\bgithub\s*actions\b'],
    "Linux": [r'\blinux\b', r'\bubuntu\b', r'\bbash\b', r'\bshell\s+scripting\b'],
    "Terraform": [r'\bterraform\b'],

    # AI, ML & Data Science
    "Machine Learning": [r'\bmachine\s+learning\b', r'\bml\b'],
    "Artificial Intelligence": [r'\bartificial\s+intelligence\b', r'\bai\b(?!\s*resume|\s*powered)'],
    "Deep Learning": [r'\bdeep\s+learning\b'],
    "Natural Language Processing (NLP)": [r'\bnlp\b', r'\bnatural\s+language\s+processing\b'],
    "Computer Vision": [r'\bcomputer\s+vision\b', r'\bopencv\b'],
    "TensorFlow": [r'\btensorflow\b'],
    "PyTorch": [r'\bpytorch\b'],
    "Scikit-Learn": [r'\bscikit[-_]learn\b', r'\bsklearn\b'],
    "Pandas": [r'\bpandas\b'],
    "NumPy": [r'\bnumpy\b'],
    "Data Analysis": [r'\bdata\s+analysis\b', r'\bdata\s+analytics\b'],
    "Tableau": [r'\btableau\b'],
    "Power BI": [r'\bpower\s*bi\b'],

    # Tools & Practices
    "Git": [r'\bgit\b(?!\s*hub)'],
    "GitHub": [r'\bgithub\b'],
    "GitLab": [r'\bgitlab\b'],
    "Jira": [r'\bjira\b'],
    "Agile": [r'\bagile\b', r'\bscrum\b'],
    "Unit Testing": [r'\bunit\s+test(?:ing)?\b', r'\bpytest\b', r'\bjunit\b']
}

def extract_skills(text):
    """
    Extract technical and professional skills from text using boundary-safe regex patterns.
    Avoids partial substring bugs (e.g. 'c' matching 'academic').
    Returns a sorted list of unique canonical skill names.
    """
    if not text:
        return []
        
    found_skills = set()
    
    for canonical_name, patterns in SKILL_TAXONOMY.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found_skills.add(canonical_name)
                break
                
    return sorted(list(found_skills))

def parse_skill_list(skill_string):
    """
    Parse a comma-separated or newline-separated skill string from a form input.
    Matches with canonical names where possible, or trims user-provided custom skills.
    """
    if not skill_string:
        return []
    raw_tokens = re.split(r'[,;\n]+', skill_string)
    parsed = []
    for token in raw_tokens:
        clean = token.strip()
        if not clean:
            continue
        matched = False
        for canonical, patterns in SKILL_TAXONOMY.items():
            if clean.lower() == canonical.lower():
                parsed.append(canonical)
                matched = True
                break
            for p in patterns:
                if re.search(p, clean, re.IGNORECASE):
                    parsed.append(canonical)
                    matched = True
                    break
            if matched:
                break
        if not matched:
            parsed.append(clean.title())
    seen = set()
    result = []
    for s in parsed:
        if s.lower() not in seen:
            seen.add(s.lower())
            result.append(s)
    return result

def compare_skills(candidate_skills, required_skills, preferred_skills=None):
    """
    Compare candidate skills against required and preferred criteria.
    """
    cand_lower = {s.lower(): s for s in candidate_skills}
    req_lower = {s.lower(): s for s in (required_skills or [])}
    pref_lower = {s.lower(): s for s in (preferred_skills or [])}

    matched_required = []
    missing_required = []
    for k, orig in req_lower.items():
        if k in cand_lower:
            matched_required.append(orig)
        else:
            missing_required.append(orig)

    matched_preferred = []
    missing_preferred = []
    for k, orig in pref_lower.items():
        if k in cand_lower:
            matched_preferred.append(orig)
        else:
            missing_preferred.append(orig)

    additional_skills = [
        s for k, s in cand_lower.items()
        if k not in req_lower and k not in pref_lower
    ]

    req_ratio = len(matched_required) / len(req_lower) if req_lower else 1.0
    pref_ratio = len(matched_preferred) / len(pref_lower) if pref_lower else 1.0

    return {
        "matched_required": sorted(matched_required),
        "missing_required": sorted(missing_required),
        "matched_preferred": sorted(matched_preferred),
        "missing_preferred": sorted(missing_preferred),
        "additional_skills": sorted(additional_skills),
        "required_ratio": req_ratio,
        "preferred_ratio": pref_ratio
    }