# File: analyzer.py
import os
import re
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()


# ----------------------------
#  Azure Client Setup
# ----------------------------
def _get_client():
    endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT")
    key = os.getenv("AZURE_LANGUAGE_KEY")

    if not endpoint or not key:
        raise ValueError("Azure credentials missing in .env")

    return TextAnalyticsClient(endpoint, AzureKeyCredential(key))


# ----------------------------
#  File Text Extraction
# ----------------------------
def extract_text(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("File not found")

    _, ext = os.path.splitext(file_path)
    text = ""

    if ext.lower() == ".pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""

    elif ext.lower() == ".docx":
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError("Invalid file format (PDF/DOCX only).")

    return text


# ----------------------------
#  Resume Analysis
# ----------------------------
def analyze_resume_text(text):
    client = _get_client()

    # 1. Extract key phrases
    try:
        kp = client.extract_key_phrases([text])[0]
        key_phrases = kp.key_phrases if not kp.is_error else []
    except:
        key_phrases = []

    # 2. Extract entities
    try:
        ent = client.recognize_entities([text])[0]
        entities = [
            {
                "text": e.text,
                "category": e.category,
                "sub": e.subcategory,
                "score": e.confidence_score,
            }
            for e in ent.entities
        ]
    except:
        entities = []

    # 3. Name, Email, Phone detection
    name = next((e["text"] for e in entities if e["category"] == "Person"), None)

    email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone = re.search(r"(\+?\d[\d\s\-]{8,}\d)", text)

    return {
        "raw_text": text,
        "name": name,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "key_phrases": key_phrases,
        "entities": entities,
    }


# ----------------------------
#  JD Matching Logic
# ----------------------------
def extract_jd_keywords(jd):
    client = _get_client()

    try:
        kp = client.extract_key_phrases([jd])[0]
        return [k.lower() for k in kp.key_phrases]
    except:
        return []


def analyze_resume_with_job(file_path, job_description):
    resume_text = extract_text(file_path)
    resume_data = analyze_resume_text(resume_text)

    jd_keywords = extract_jd_keywords(job_description)
    resume_words = resume_text.lower()

    matched = [k for k in jd_keywords if k in resume_words]
    missing = [k for k in jd_keywords if k not in resume_words]

    match_percentage = int((len(matched) / len(jd_keywords)) * 100) if jd_keywords else 0

    # Section checks
    sections = ["skills", "education", "experience", "projects", "certification"]
    missing_sections = [s.capitalize() for s in sections if s not in resume_words]

    # Suggestions
    suggestions = []

    if missing:
        suggestions.append(f"Consider including missing JD keywords: {', '.join(missing[:10])}")

    if missing_sections:
        suggestions.append(f"Your resume is missing these sections: {', '.join(missing_sections)}")

    if match_percentage < 60:
        suggestions.append("Your resume match score is low; tailor your resume to the job description.")

    if not suggestions:
        suggestions.append("Great! Your resume is well aligned with the job description.")

    # Final combined result
    resume_data.update({
        "job_description": job_description,
        "job_keywords": jd_keywords,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "missing_sections": missing_sections,
        "match_percentage": match_percentage,
        "suggestions": suggestions,
    })

    return resume_data
