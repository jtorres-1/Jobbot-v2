import pdfplumber
import re

def parse_resume(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "raw_text": text,
        "pdf_path": pdf_path
    }

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else ""

def extract_phone(text):
    match = re.search(r'(\+?1?\s?)?(\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4})', text)
    return match.group(0) if match else ""

def extract_name(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return lines[0] if lines else ""

def extract_skills(text):
    common_skills = [
        "python", "javascript", "typescript", "react", "node", "flask", "django",
        "sql", "postgresql", "mysql", "mongodb", "aws", "docker", "kubernetes",
        "git", "linux", "java", "c++", "c#", "html", "css", "rest", "api",
        "machine learning", "data analysis", "excel", "figma", "photoshop"
    ]
    text_lower = text.lower()
    return [s for s in common_skills if s in text_lower]
