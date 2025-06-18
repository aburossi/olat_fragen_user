# app.py

"""
Main entry point for the Streamlit OLAT Question Generator application.
This script initializes the app and coordinates the UI, file processing, and logic modules.
"""

import streamlit as st
import logging
from ui import render_sidebar, render_main_page, apply_custom_css
from config import MESSAGE_TYPES, ZIELNIVEAUS_MAP, LANGUAGES, MODEL_OPTIONS
from file_processing import process_uploaded_files
from openai_client import initialize_client
from logic import generate_questions

# --- Page Configuration ---
st.set_page_config(
    page_title="📝 OLAT Fragen Generator",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Initialize Logging ---
logging.basicConfig(level=logging.INFO)

def main():
    """Main function to run the Streamlit application."""
    
    # --- UI Rendering ---
    apply_custom_css()
    render_sidebar()
    st.title("📝 Fragen Generator")

    # --- API Key and Client Initialization ---
    api_key = st.text_input("🔑 Geben Sie Ihren OpenAI-API-Schlüssel ein", type="password", help="Ihr Schlüssel wird nicht gespeichert.")
    client = initialize_client(api_key)

    # --- Model, Language, and Level Selection ---
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_model = st.selectbox("Modell:", MODEL_OPTIONS, index=0)
    with col2:
        selected_language_key = st.radio("Sprache:", list(LANGUAGES.keys()), index=0, horizontal=True)
        selected_language = LANGUAGES[selected_language_key]
    with col3:
        if selected_model == "o4-mini":
            reasoning_effort = st.selectbox("Reasoning Effort:", ["low", "medium", "high"], index=1)
        else:
            reasoning_effort = "medium" # Default for other models

    zielniveau_labels = list(ZIELNIVEAUS_MAP.keys())
    selected_zielniveau_label = st.radio(
        "Zielniveau:", zielniveau_labels, index=2, horizontal=True,
        help="Bestimmt die sprachliche Komplexität der Fragen."
    )
    selected_zielniveau_text = ZIELNIVEAUS_MAP[selected_zielniveau_label]

    # --- File Upload and Processing ---
    uploaded_files = st.file_uploader(
        "Laden Sie Inhalt hoch (1 PDF/DOCX oder bis zu 10 Bilder)",
        type=["pdf", "docx", "jpg", "jpeg", "png"],
        accept_multiple_files=True
    )
    
    text_content = ""
    image_content_list = []
    if uploaded_files:
        with st.spinner("Dateien werden verarbeitet..."):
            text_content, image_content_list = process_uploaded_files(uploaded_files)

    # --- User Input Fields ---
    if image_content_list:
        st.success(f"{len(image_content_list)} Bild(er) erfolgreich geladen und verarbeitet.")
        cols = st.columns(min(len(image_content_list), 5))
        for idx, img in enumerate(image_content_list):
            cols[idx % 5].image(img, use_column_width=True, caption=f"Bild {idx + 1}")

    user_input = st.text_area("Text zum Analysieren:", value=text_content, height=250, help="Fügen Sie hier Ihren Text ein oder er wird aus der hochgeladenen Datei extrahiert.")
    learning_goals = st.text_area("Lernziele (Optional):", height=100, help="Definieren Sie spezifische Lernziele, um die Fragengenerierung zu steuern.")
    selected_types = st.multiselect("Wählen Sie die Fragetypen:", MESSAGE_TYPES)

    # --- Generation Button and Logic Execution ---
    if st.button("🚀 Fragen generieren", type="primary"):
        if not client:
            st.error("Bitte geben Sie zuerst Ihren OpenAI-API-Schlüssel ein.")
        elif not (user_input or image_content_list):
            st.warning("Bitte geben Sie Text ein oder laden Sie eine Datei hoch.")
        elif not selected_types:
            st.warning("Bitte wählen Sie mindestens einen Fragetyp aus.")
        else:
            generate_questions(
                client=client,
                user_input=user_input,
                learning_goals=learning_goals,
                selected_types=selected_types,
                images=image_content_list,
                selected_language=selected_language,
                selected_model=selected_model,
                reasoning_effort=reasoning_effort,
                selected_zielniveau=selected_zielniveau_text
            )

if __name__ == "__main__":
    main()