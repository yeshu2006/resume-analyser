# File: app.py
import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from resume_parser import extract_text_from_resume
from analyzer import analyze_resume_text

app = Flask(__name__)

@app.route('/')
def index():
    """Renders the main upload page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handles the file upload and analysis logic."""
    if 'resume' not in request.files:
        return render_template('index.html', error="No resume file was submitted.")
    
    resume_file = request.files['resume']
    job_description = request.form['job_description']

    if resume_file.filename == '':
        return render_template('index.html', error="No resume file was selected.")

    if resume_file and job_description:
        filename = secure_filename(resume_file.filename)
        
        # --- Diagnostic printing to the terminal for debugging ---
        print(f"--- Analyzing file: {filename} ---")
        
        # Process the file stream directly without saving
        resume_text = extract_text_from_resume(resume_file.stream, filename)
        
        print(f"--- Text extraction complete. Length: {len(resume_text)} chars ---")

        # If text extraction failed, show an error on the page
        if not resume_text.strip():
            error_msg = "Could not read the resume. Please use a text-based PDF or DOCX file (not an image)."
            return render_template('index.html', error=error_msg)

        # Send the extracted text to the analyzer module
        analysis_result = analyze_resume_text(resume_text, job_description)

        # Render the same page, but now with the results dictionary
        return render_template('index.html', results=analysis_result)

    return render_template('index.html', error="An unexpected error occurred.")

if __name__ == '__main__':
    # Runs the web server in debug mode for development
    app.run(debug=True)
