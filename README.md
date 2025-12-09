# Resume Analyser

A simple AI-powered Resume Analyzer built with Python and Azure AI services that extracts and evaluates key information from resumes to assist recruiters in faster screening.

## 🔍 Features

- Upload resume (PDF/Text/DOCX)
- Extracts: Name, Contact Info, Skills, Experience, Education
- Named Entity Recognition (NER) to identify key entities like organizations, locations, and skills.
- Uses **Azure AI Document Intelligence** (Form Recognizer) for extraction
- Web interface using **Flask**
- Live deployment on **Render**

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **AI Service**: Azure AI Document Intelligence, Azure Text Analytics
- **Frontend**: HTML, CSS
- **Deployment**: [Render](https://render.com/)

## 🔑 Environment Variables

To run this project, you will need to add the following environment variables to your .env file:

`AZURE_LANGUAGE_ENDPOINT`
`AZURE_LANGUAGE_KEY`

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yeshu2006/resume-analyser.git
cd resume-analyser

```