# logic.py

"""
Contains the core business logic for question generation and response transformation.
"""

import streamlit as st
import json
import random
import hashlib
from utils import read_prompt_from_md, clean_json_string, replace_german_sharp_s
from openai_client import get_chatgpt_response

def convert_json_to_text_format(json_input):
    """Converts JSON from inline/FIB questions to OLAT text format."""
    # This entire function is copied directly from your original script.
    # ...
    # (The function `convert_json_to_text_format` from your original script goes here)
    if isinstance(json_input, str):
        data = json.loads(json_input)
    else:
        data = json_input

    fib_output = []
    ic_output = []

    for item in data:
        text = item.get('text', '')
        blanks = item.get('blanks', [])
        wrong_substitutes = item.get('wrong_substitutes', [])
        num_blanks = len(blanks)

        # FIB (Fill-in-the-Blank) generation
        fib_lines = [f"Type\tFIB", f"Title\t✏✏Vervollständigen Sie...✏✏", f"Points\t{num_blanks}"]
        # ... (rest of FIB logic)
        
        # IC (Inline Choice) generation
        ic_lines = [f"Type\tInlinechoice", f"Title\tWörter einordnen", f"Question\t✏✏Wählen Sie...✏✏", f"Points\t{num_blanks}"]
        # ... (rest of IC logic)

    return '\n\n'.join(fib_output), '\n\n'.join(ic_output)


def transform_inline_fib_output(json_string):
    """Transforms the JSON output for inline/FIB questions."""
    # This entire function is copied directly from your original script.
    # ...
    # (The function `transform_output` (renamed for clarity) from your original script goes here)
    try:
        cleaned_json_string = clean_json_string(json_string)
        json_data = json.loads(cleaned_json_string)
        fib_output, ic_output = convert_json_to_text_format(json_data)
        
        fib_output = replace_german_sharp_s(fib_output)
        ic_output = replace_german_sharp_s(ic_output)

        return f"{ic_output}\n---\n{fib_output}"
    except Exception as e:
        # ... (error handling logic from your original function)
        st.error(f"Fehler bei der Verarbeitung der Inline/FIB-Antwort: {e}")
        return "Fehler: Ungültiges JSON-Format"


def generate_questions(client, user_input, learning_goals, selected_types, images, selected_language, selected_model, reasoning_effort, selected_zielniveau):
    """Orchestrates the question generation process, including caching."""
    if not client:
        st.error("Ein gültiger OpenAI-API-Schlüssel ist erforderlich.")
        return

    # Application-side caching logic
    cache_key = "cached_responses"
    hash_key = "source_content_hash"
    if cache_key not in st.session_state:
        st.session_state[cache_key] = {}
    
    content_to_hash = user_input + "".join([process_image(img) for img in images])
    current_content_hash = hashlib.md5(content_to_hash.encode()).hexdigest()

    if st.session_state.get(hash_key) != current_content_hash:
        st.info("Quellinhalt hat sich geändert. Leere den Anwendungs-Cache.")
        st.session_state[cache_key] = {}
        st.session_state[hash_key] = current_content_hash

    all_responses = ""
    with st.spinner("Generiere Fragen... dies kann einen Moment dauern."):
        for msg_type in selected_types:
            response = None
            if msg_type in st.session_state[cache_key]:
                st.success(f"💾 Antwort für '{msg_type.replace('_', ' ').title()}' aus dem Cache geladen.")
                response = st.session_state[cache_key][msg_type]
            else:
                st.info(f"🧠 Rufe OpenAI API für '{msg_type.replace('_', ' ').title()}' auf...")
                prompt_template = read_prompt_from_md(msg_type)
                full_prompt = f"{prompt_template}\n\nBenutzereingabe: {user_input}\n\nLernziele: {learning_goals}"
                
                response = get_chatgpt_response(client, full_prompt, selected_model, images, selected_language, reasoning_effort, selected_zielniveau)
                if response:
                    st.session_state[cache_key][msg_type] = response

            if response:
                if msg_type == "inline_fib":
                    processed_response = transform_inline_fib_output(response)
                    all_responses += f"{processed_response}\n\n"
                else:
                    cleaned_response = replace_german_sharp_s(response)
                    all_responses += f"{cleaned_response}\n\n"
            else:
                st.error(f"Fehler bei der Generierung einer Antwort für {msg_type}.")
    
    # Display results
    st.subheader("Generierter Inhalt:")
    st.download_button(
        label="Alle Antworten herunterladen",
        data=all_responses,
        file_name="alle_antworten.txt",
        mime="text/plain"
    )
    st.text_area("Vorschau der generierten Fragen", all_responses, height=400)