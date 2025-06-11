# File: resume_parser.py
import pypdf
import docx
import os

def extract_text_from_resume(file_stream, file_name):
    """
    Extracts text from a resume file (PDF or DOCX).
    Includes robust error handling.
    """
    text = ""
    # Get the file's extension to determine how to read it
    _, extension = os.path.splitext(file_name)

    try:
        if extension.lower() == ".pdf":
            reader = pypdf.PdfReader(file_stream)
            for page in reader.pages:
                # Add page text, using 'or ""' to prevent errors if a page is empty
                text += page.extract_text() or ""
        elif extension.lower() == ".docx":
            doc = docx.Document(file_stream)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            # A fallback for other file types, like .txt
            text = file_stream.read().decode('utf-8')
    except Exception as e:
        # If any library fails to read the file, print an error and return nothing.
        # This prevents the application from crashing.
        print(f"!!! ERROR IN PARSER: Could not process file {file_name}. Reason: {e}")
        return ""

    return text
