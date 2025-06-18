# utils.py

"""
Contains utility functions for image processing, text cleaning, and file reading.
"""

import streamlit as st
import os
import io
import base64
import re
from PIL import Image

@st.cache_data
def read_prompt_from_md(filename):
    """Reads a prompt from a markdown file and caches the result."""
    file_path = os.path.join("prompts", f"{filename}.md")
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def process_image(_image):
    """
    Processes and resizes an image to reduce memory usage, returning a base64 string.
    This function now correctly handles file paths, bytes, PIL.Image objects, and Streamlit's UploadedFile.
    """
    img = None
    # --- START OF FIX ---
    # Check if the input is already a PIL Image object.
    if isinstance(_image, Image.Image):
        img = _image
    # Check if the input is a file path (string) or raw bytes.
    elif isinstance(_image, (str, bytes)):
        img = Image.open(io.BytesIO(base64.b64decode(_image) if isinstance(_image, str) else _image))
    # Otherwise, assume it's a file-like object (e.g., from st.file_uploader)
    else:
        img = Image.open(_image)
    # --- END OF FIX ---

    # Convert to RGB mode if necessary (e.g., for PNGs with transparency)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize the image if it's too large to save tokens and processing time
    max_size = 1024
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size))

    # Save the processed image to an in-memory byte buffer
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=85)
    
    # Return the image as a base64 encoded string
    return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')


def replace_german_sharp_s(text):
    """Replaces all occurrences of 'ß' with 'ss'."""
    return text.replace('ß', 'ss')


def clean_json_string(s):
    """Cleans and repairs a string to ensure it is valid JSON."""
    s = s.strip()
    s = re.sub(r'^```json\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'```\s*$', '', s)
    s = s.strip()
    match = re.search(r'\[.*\]', s, re.DOTALL)
    if not match:
        match = re.search(r'\{.*\}', s, re.DOTALL)
    return match.group(0) if match else s