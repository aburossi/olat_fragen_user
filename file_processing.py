# file_processing.py

"""
Handles processing of uploaded files like PDF, DOCX, and images.
"""

import streamlit as st
import io
import PyPDF2
import docx
from pdf2image import convert_from_bytes
from PIL import Image

@st.cache_data
def extract_text_from_pdf(file_bytes):
    """Extracts text from a PDF file using PyPDF2."""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
    return text.strip()

@st.cache_data
def extract_text_from_docx(file_bytes):
    """Extracts text from a DOCX file."""
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([paragraph.text for paragraph in doc.paragraphs]).strip()

@st.cache_data
def convert_pdf_to_images(_file_bytes):
    """Converts PDF pages to a list of PIL Image objects."""
    return convert_from_bytes(_file_bytes)

def process_uploaded_files(uploaded_files):
    """Processes uploaded files, extracting text and images."""
    text_content = ""
    image_content_list = []

    # File validation
    if len(uploaded_files) > 10:
        st.error("Bitte laden Sie maximal 10 Bilder hoch.")
        return None, None
    
    has_doc = any(f.name.lower().endswith(('.pdf', '.docx')) for f in uploaded_files)
    has_img = any(f.type.startswith('image/') for f in uploaded_files)
    
    if has_doc and has_img and len(uploaded_files) > 1:
        st.error("Sie können entweder eine einzelne PDF/DOCX-Datei oder mehrere Bilddateien hochladen, nicht beides mischen.")
        return None, None
    if len([f for f in uploaded_files if has_doc]) > 1:
        st.error("Bitte laden Sie nur eine einzelne PDF- oder DOCX-Datei hoch.")
        return None, None

    # Process files
    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.getvalue()
        if uploaded_file.type == "application/pdf":
            text_from_pdf = extract_text_from_pdf(file_bytes)
            if text_from_pdf:
                text_content += text_from_pdf + "\n\n"
            else:
                st.warning("Kein extrahierbarer Text im PDF gefunden. Es wird versucht, das PDF als Bilder zu verarbeiten.")
                image_content_list.extend(convert_pdf_to_images(file_bytes))
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text_content += extract_text_from_docx(file_bytes) + "\n\n"
        elif uploaded_file.type.startswith('image/'):
            image_content_list.append(Image.open(io.BytesIO(file_bytes)))

    return text_content.strip(), image_content_list