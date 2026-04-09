# File: app.py
import os
import tempfile
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from analyzer import analyze_resume_with_job

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", result=None, job_description="")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        flash("No file uploaded.")
        return redirect(url_for("index"))

    resume = request.files["resume"]
    jd = request.form.get("job_description", "").strip()

    if resume.filename == "":
        flash("Please select a resume file.")
        return redirect(url_for("index"))

    if not allowed_file(resume.filename):
        flash("Only PDF and DOCX files are allowed.")
        return redirect(url_for("index"))

    if not jd:
        flash("Please paste a Job Description for matching.")
        return redirect(url_for("index"))

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(resume.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    resume.save(file_path)

    try:
        result = analyze_resume_with_job(file_path, jd)
        return render_template("index.html", result=result, job_description=jd)
    except Exception as e:
        print("ERROR:", e)
        flash(f"An error occurred while analyzing the resume: {e}")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)