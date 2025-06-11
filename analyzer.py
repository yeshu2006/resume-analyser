# File: analyzer.py (Corrected Advanced Version)

import os
import re
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
# --- Import the specific action class ---
from azure.ai.textanalytics import TextAnalyticsClient, ExtractKeyPhrasesAction

load_dotenv()

def analyze_resume_text(resume_text, jd_text):
    """
    Analyzes resume against a job description using the 'begin_analyze_actions'
    long-running operation pattern.
    """
    try:
        endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
        key = os.environ["AZURE_LANGUAGE_KEY"]
    except KeyError:
        return {"error": "Azure credentials not found. Ensure .env file is set up correctly."}

    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    
    documents = [resume_text, jd_text]

    try:
        # --- Use the correct method name: begin_analyze_actions ---
        poller = text_analytics_client.begin_analyze_actions(
            documents,
            actions=[
                ExtractKeyPhrasesAction() # Specify the action you want to perform
            ],
        )

        document_results = poller.result()
        
        resume_phrases = set()
        jd_phrases = set()

        # --- Loop through the results to find the key phrases ---
        for doc, action_results in zip(documents, document_results):
            for result in action_results:
                if result.kind == "KeyPhraseExtraction":
                    if documents.index(doc) == 0: # First document is the resume
                        resume_phrases = set(phrase.lower() for phrase in result.key_phrases)
                    else: # Second document is the job description
                        jd_phrases = set(phrase.lower() for phrase in result.key_phrases)
                elif result.is_error is True:
                     return {"error": f"Azure API Error: '{result.error.code}' - '{result.error.message}'"}

    except Exception as e:
        return {"error": f"An unexpected Azure API Error occurred: {str(e)}"}

    # --- Comparison and formatting section remains the same ---
    matched_skills = sorted(list(resume_phrases.intersection(jd_phrases)))
    missing_skills = sorted(list(jd_phrases.difference(resume_phrases)))

    # (The rest of the function is identical to the simple version...)
    formatting_suggestions = []
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text):
        formatting_suggestions.append("Actionable Tip: Add a professional email address.")
    if not re.search(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{10})', resume_text):
        formatting_suggestions.append("Actionable Tip: Add a phone number.")
    if len(resume_text.split()) > 700:
        formatting_suggestions.append("Content Suggestion: Your resume seems long. Aim for conciseness (450-650 words is ideal).")

    try:
        match_percentage = (len(matched_skills) / len(jd_phrases)) * 100 if jd_phrases else 100
    except ZeroDivisionError:
        match_percentage = 100

    return {
        "match_score": f"{match_percentage:.1f}%",
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "formatting_suggestions": formatting_suggestions
    }
