# -*- coding: utf-8 -*-
"""Resume_job_maker.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1g2L06AY1HNRCcX_BUWuvtxKx72OG1xH5
"""

# Step 1: Install dependencies (Uncomment the next line if not already installed)
!pip install gradio sentence-transformers PyMuPDF

# Step 2: Import libraries
import gradio as gr
from sentence_transformers import SentenceTransformer, util
import fitz  # PyMuPDF
import os

# Step 3: Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Step 4: Extract text from PDF or .txt
def extract_text(filepath):
    if filepath.endswith(".pdf"):
        text = ""
        try:
            doc = fitz.open(filepath)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            return f"⚠️ Error reading PDF: {str(e)}"
        return text.strip()

    elif filepath.endswith(".txt"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            return f"⚠️ Error reading TXT file: {str(e)}"
    else:
        return "⚠️ Unsupported file type. Please upload a PDF or TXT."

# Step 5: Core analyzer
def analyze_resume_job(resume_file, job_file):
    if not resume_file or not job_file:
        return "Please upload both files.", "", "", ""

    resume_path = resume_file.name
    job_path = job_file.name

    resume_text = extract_text(resume_path)
    job_text = extract_text(job_path)

    if resume_text.startswith("⚠️") or job_text.startswith("⚠️"):
        return resume_text if resume_text.startswith("⚠️") else job_text, "", "", ""

    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    job_emb = model.encode(job_text, convert_to_tensor=True)

    similarity = util.cos_sim(resume_emb, job_emb).item()
    score = round(similarity * 100, 2)

    # Optional: Keyword matching for simple skills extraction
    common_keywords = []
    for word in job_text.lower().split():
        if word in resume_text.lower() and word.isalpha() and len(word) > 4:
            common_keywords.append(word)
    matched_keywords = list(set(common_keywords))

    return (
        f"🔍 Compatibility Score: {score}%",
        f"✅ Matched Keywords:\n{', '.join(matched_keywords[:10]) if matched_keywords else 'None found'}",
        f"📄 Resume Snippet:\n{resume_text[:500]}...",
        f"📝 Job Snippet:\n{job_text[:500]}..."
    )

# Step 6: Gradio UI
interface = gr.Interface(
    fn=analyze_resume_job,
    inputs=[
        gr.File(label="Upload Resume (.pdf or .txt)", file_types=[".pdf", ".txt"]),
        gr.File(label="Upload Job Description (.pdf or .txt)", file_types=[".pdf", ".txt"])
    ],
    outputs=[
        gr.Text(label="Compatibility Score"),
        gr.Text(label="Matched Keywords"),
        gr.Text(label="Resume Snippet"),
        gr.Text(label="Job Snippet")
    ],
    title="EduCareer Match – AI Resume & JD Analyzer",
    description="📂 Upload your resume and a job description to get a compatibility score, matched skills, and personalized guidance."
)

interface.launch()