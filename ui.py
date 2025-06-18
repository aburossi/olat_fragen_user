# ui.py

"""
Defines the user interface components of the Streamlit application.
"""

import streamlit as st
import streamlit.components.v1 as components

def apply_custom_css():
    """Applies custom CSS for light mode and callouts."""
    st.markdown("""
        <style>
            /* Force light mode */
            body, .css-18e3th9, .css-1d391kg {
                background-color: white;
                color: black;
            }
            .custom-info { background-color: #e7f3fe; padding: 10px; border-radius: 5px; border-left: 6px solid #2196F3; }
            .custom-success { background-color: #d4edda; padding: 10px; border-radius: 5px; border-left: 6px solid #28a745; }
            .custom-warning { background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 6px solid #ffc107; }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renders the sidebar with instructions, information, and contact details."""
    with st.sidebar:
        st.header("❗ **So verwenden Sie diese App**")
        st.markdown("""
            1. **Geben Sie Ihren OpenAI-API-Schlüssel ein**...
            2. **Laden Sie eine PDF, DOCX oder bis zu 10 Bilder hoch**...
            3. **Sprache auswählen**...
            4. **Fragetypen auswählen**...
            5. **Fragen generieren**...
            6. **Generierte Inhalte herunterladen**...
        """)
        # ... (All other st.markdown, components.html, etc. from your original sidebar go here)

        st.header("💬 Kontakt")
        st.markdown("Für Unterstützung... **Kontakt**: [Pietro](mailto:pietro.rossi@bbw.ch)")

def render_main_page(text_from_files, images_from_files):
    """Renders the main content area of the application."""
    st.title("📝 Fragen Generator")

    api_key = st.text_input("🔑 Geben Sie Ihren OpenAI-API-Schlüssel ein", type="password")

    st.subheader("Modell, Sprache und Niveau auswählen")
    # ... (All widgets for model, language, and level selection from your `main` function go here)

    st.subheader("Inhalt hochladen oder einfügen")
    uploaded_files = st.file_uploader(
        "Laden Sie eine PDF, DOCX oder bis zu 10 Bilder hoch",
        type=["pdf", "docx", "jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if images_from_files:
        st.success(f"{len(images_from_files)} Bild(er) erfolgreich geladen.")
        cols = st.columns(min(len(images_from_files), 5))
        for idx, img in enumerate(images_from_files):
            cols[idx % 5].image(img, use_column_width=True, caption=f"Bild {idx+1}")

    user_input = st.text_area("Geben Sie Ihren Text ein oder fügen Sie den extrahierten Text hier ein:", value=text_from_files, height=300)
    learning_goals = st.text_area("Lernziele (Optional):", help="Beschreiben Sie, was die Lernenden nach Beantwortung der Fragen wissen oder können sollen.")
    
    # ... (multiselect for question types)

    return api_key, uploaded_files, user_input, learning_goals # ... and other selected values