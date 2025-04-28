import spacy
import streamlit as st
import docx
import PyPDF2
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to preprocess text
def preprocess_text(text):
    doc = nlp(text)
    return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]

# Function to extract keywords using Named Entity Recognition (NER)
def extract_keywords(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents]

# Function to calculate similarity between resume and job description
def calculate_similarity(resume_text, job_description_text):
    resume_doc = nlp(resume_text)
    job_description_doc = nlp(job_description_text)
    return resume_doc.similarity(job_description_doc)

# Function to calculate keyword overlap score
def calculate_keyword_overlap(resume_keywords, job_description_keywords):
    overlap = set(resume_keywords).intersection(set(job_description_keywords))
    return len(overlap) / len(set(job_description_keywords))  # Matching score as a percentage

# Function to extract years or work experience mentions
def extract_years(text):
    # Search for patterns like "5 years", "2 years ago", etc.
    year_pattern = r"(\d{1,2})\s*(years?|yr)"
    return re.findall(year_pattern, text)

# Function to analyze match
def analyze_match(resume_text, job_description_text):
    resume_keywords = extract_keywords(resume_text)
    job_description_keywords = extract_keywords(job_description_text)

    similarity = calculate_similarity(resume_text, job_description_text)
    keyword_overlap = calculate_keyword_overlap(resume_keywords, job_description_keywords)

    # Extract years from both resume and job description
    resume_years = extract_years(resume_text)
    job_desc_years = extract_years(job_description_text)

    # Combine the scores (you can give weights to each part as needed)
    overall_score = (similarity + keyword_overlap) / 2
    return overall_score, resume_keywords, job_description_keywords, resume_years, job_desc_years

# Function to read .txt files
def read_txt(file):
    return file.read().decode("utf-8")

# Function to read .docx files
def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# Function to read .pdf files
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

# Streamlit UI setup
st.title("Resume and Job Description Matcher")

st.write("Enter your resume and job description below to calculate the match score.")

# File upload for resume and job description
resume_file = st.file_uploader("Upload your Resume (txt, docx, or pdf)", type=["txt", "docx", "pdf"])
job_desc_file = st.file_uploader("Upload the Job Description (txt, docx, or pdf)", type=["txt", "docx", "pdf"])

# Read file contents
if resume_file and job_desc_file:
    if resume_file.type == "text/plain":
        resume_text = read_txt(resume_file)
    elif resume_file.type == "application/pdf":
        resume_text = read_pdf(resume_file)
    elif resume_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        resume_text = read_docx(resume_file)
    
    if job_desc_file.type == "text/plain":
        job_desc_text = read_txt(job_desc_file)
    elif job_desc_file.type == "application/pdf":
        job_desc_text = read_pdf(job_desc_file)
    elif job_desc_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        job_desc_text = read_docx(job_desc_file)

    # Button to trigger analysis
    if st.button("Analyze Match"):
        if resume_text and job_desc_text:
            score, resume_keywords, job_desc_keywords, resume_years, job_desc_years = analyze_match(resume_text, job_desc_text)

            st.write(f"### Match Score: {score:.2f}")
            
            st.write("#### Keywords in Resume:")
            st.write(resume_keywords)
            
            st.write("#### Keywords in Job Description:")
            st.write(job_desc_keywords)
            
            st.write("#### Common Keywords:")
            st.write(set(resume_keywords).intersection(set(job_desc_keywords)))
            
            st.write("#### Years/Experience Mentioned in Resume:")
            st.write(resume_years)
            
            st.write("#### Years/Experience Mentioned in Job Description:")
            st.write(job_desc_years)

        else:
            st.error("Please upload both resume and job description files.")

