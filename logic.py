# logic.py

"""
Contains the core business logic for question generation and response transformation.
"""

import streamlit as st
import json
import random
import hashlib
# The fix is on the next line: adding 'process_image' to the import list
from utils import read_prompt_from_md, clean_json_string, replace_german_sharp_s, process_image
from openai_client import get_chatgpt_response

def convert_json_to_text_format(json_input):
    """Converts JSON from inline/FIB questions to OLAT text format."""
    if isinstance(json_input, str):
        try:
            data = json.loads(json_input)
        except json.JSONDecodeError:
            st.error("Fehler beim Dekodieren des JSON-Strings in 'convert_json_to_text_format'.")
            return "", ""
    else:
        data = json_input

    fib_output = []
    ic_output = []

    for item in data:
        text = item.get('text', '')
        blanks = item.get('blanks', [])
        wrong_substitutes = item.get('wrong_substitutes', [])
        num_blanks = len(blanks)

        # --- FIB (Fill-in-the-Blank) Generation ---
        fib_lines = [
            "Type\tFIB",
            "Title\t✏️ Vervollständigen Sie die Lücken mit dem korrekten Begriff. ✏️",
            f"Points\t{num_blanks}"
        ]
        placeholder = "||BLANK||"
        original_text = text
        for blank in blanks:
            original_text = original_text.replace(blank, placeholder, 1)

        parts = original_text.split(placeholder)
        for index, part in enumerate(parts):
            fib_lines.append(f"Text\t{part.strip()}")
            if index < len(blanks):
                fib_lines.append(f"1\t{blanks[index]}\t20")
        fib_output.append('\n'.join(fib_lines))

        # --- IC (Inline Choice) Generation ---
        ic_lines = [
            "Type\tInlinechoice",
            "Title\tWörter einordnen",
            "Question\t✏️ Wählen Sie die richtigen Wörter. ✏️",
            f"Points\t{num_blanks}"
        ]
        all_options = blanks + wrong_substitutes
        random.shuffle(all_options)

        for index, part in enumerate(parts):
            ic_lines.append(f"Text\t{part.strip()}")
            if index < len(blanks):
                options_str = '|'.join(all_options)
                ic_lines.append(f"1\t{options_str}\t{blanks[index]}\t|")
        ic_output.append('\n'.join(ic_lines))

    return '\n\n'.join(fib_output), '\n\n'.join(ic_output)


def transform_inline_fib_output(json_string):
    """Transforms the JSON output for inline/FIB questions."""
    try:
        cleaned_json_string = clean_json_string(json_string)
        json_data = json.loads(cleaned_json_string)
        fib_output, ic_output = convert_json_to_text_format(json_data)

        fib_output = replace_german_sharp_s(fib_output)
        ic_output = replace_german_sharp_s(ic_output)

        return f"{ic_output}\n---\n{fib_output}"
    except json.JSONDecodeError as e:
        st.error(f"Fehler beim Parsen von JSON in 'transform_inline_fib_output': {e}")
        st.text_area("Fehlerhafter JSON-String", json_string)
        return "Fehler: Ungültiges JSON-Format erhalten."
    except Exception as e:
        st.error(f"Ein unerwarteter Fehler ist in 'transform_inline_fib_output' aufgetreten: {e}")
        return "Fehler: Eingabe konnte nicht verarbeitet werden."


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

    # Create a hash of the current source content to detect changes
    content_to_hash = user_input
    if images:
        # This line now works because process_image is imported
        content_to_hash += "".join([process_image(img) for img in images])
    current_content_hash = hashlib.md5(content_to_hash.encode()).hexdigest()

    if st.session_state.get(hash_key) != current_content_hash:
        st.info("Quellinhalt hat sich geändert. Leere den Anwendungs-Cache.")
        st.session_state[cache_key] = {}
        st.session_state[hash_key] = current_content_hash

    all_responses = ""
    generated_content = {}
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
                    generated_content[f"{msg_type.replace('_', ' ').title()} (Verarbeitet)"] = processed_response
                    all_responses += f"{processed_response}\n\n"
                else:
                    cleaned_response = replace_german_sharp_s(response)
                    generated_content[msg_type.replace('_', ' ').title()] = cleaned_response
                    all_responses += f"{cleaned_response}\n\n"
            else:
                st.error(f"Fehler bei der Generierung einer Antwort für {msg_type}.")

    # Display results
    st.subheader("Generierter Inhalt:")
    for title in generated_content:
        st.write(f"✔️ {title}")

    if all_responses:
        st.download_button(
            label="Alle Antworten herunterladen",
            data=all_responses,
            file_name="alle_antworten.txt",
            mime="text/plain"
        )
        st.text_area("Vorschau der generierten Fragen", all_responses, height=400)