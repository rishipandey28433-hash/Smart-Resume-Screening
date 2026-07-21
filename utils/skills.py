def extract_skills(text):

    skills = [
        "Python",
        "Java",
        "C",
        "C++",
        "SQL",
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Node.js",
        "Express",
        "MongoDB",
        "Git",
        "GitHub",
        "Flask",
        "Machine Learning",
        "Artificial Intelligence",
        "Deep Learning",
        "Data Analysis",
        "Docker",
        "AWS"
    ]

    found = []

    text = text.lower()

    for skill in skills:

        if skill.lower() in text:

            found.append(skill)

    return sorted(found)