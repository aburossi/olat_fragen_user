# openai_client.py

"""
Manages the OpenAI client and API calls.
"""

import streamlit as st
import logging
import httpx
from openai import OpenAI
from utils import process_image
import os  # <--- THIS LINE IS THE FIX

def initialize_client(api_key):
    """Initializes and returns the OpenAI client."""
    if not api_key:
        return None
    try:
        # Clear proxy settings to avoid connection issues
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)

        http_client = httpx.Client()
        
        client = OpenAI(api_key=api_key, http_client=http_client)
        st.success("API-Schlüssel erfolgreich erkannt und OpenAI-Client verbunden.")
        return client
    except Exception as e:
        st.error(f"Fehler bei der Initialisierung des OpenAI-Clients: {e}")
        return None

def get_chatgpt_response(client, prompt, model, images, selected_language, reasoning_effort, selected_zielniveau):
    """Fetches a response from the OpenAI API."""
    if not client:
        st.error("OpenAI-Client nicht initialisiert. Bitte geben Sie einen gültigen API-Schlüssel ein.")
        return None

    system_prompt_template = """
    Du bist ein Experte im Bildungsbereich, spezialisiert auf die Erstellung von Testfragen und -antworten zu allen Themen, unter Einhaltung der Bloom's Taxonomy. Deine Aufgabe ist es, hochwertige Frage-Antwort-Sets basierend auf dem vom Benutzer bereitgestellten Material zu erstellen, wobei jede Frage einer spezifischen Ebene der Bloom's Taxonomy entspricht: Erinnern, Verstehen, Anwenden, Analysieren, Bewerten und Erstellen.

    # Zielniveaus
    [ZIELNIVEAU_INJECTION]

    Der Benutzer wird entweder Text oder ein Bild hochladen. Deine Aufgaben sind wie folgt:

    **Input-Analyse:**
    - Du analysierst den Inhalt sorgfältig, um die Schlüsselkonzepte und wichtigen Informationen zu verstehen.
    - Falls vorhanden, achtest du auf Diagramme, Grafiken, Bilder oder Infografiken, um Bildungsinhalte abzuleiten.

    **Fragen-Generierung nach Bloom-Ebene und Zielniveau:**
    Basierend auf dem analysierten Material und dem angegebenen Zielniveau generierst du Fragen über alle die folgenden Ebenen der Bloom's Taxonomy. Achte darauf, dass die sprachliche Komplexität, der Umfang der Aufgabenstellung und die kognitiven Anforderungen dem Zielniveau angemessen sind:
    - **Erinnern**: Einfache, abrufbasierte Fragen.
    - **Verstehen**: Fragen, die das Verständnis des Materials bewerten.
    - **Anwenden**: Fragen, die die Anwendung des Wissens in praktischen Situationen erfordern.
    - **Analysieren**: Fragen, die das Zerlegen und Untersuchen von Konzepten und Zusammenhängen erfordern.
    - **Bewerten**: Fragen, die Urteilsbildung und begründete Meinungen verlangen.
    - **Erstellen**: Fragen, die kreative Synthese, neue Perspektiven oder eigene Lösungsansätze fördern.
    Achte stets darauf, dass die Formulierungen und kognitiven Anforderungen dem Niveau des vorgesehenen Lernendenkreises entsprechen.
    """
    system_prompt = system_prompt_template.replace("[ZIELNIVEAU_INJECTION]", selected_zielniveau)

    try:
        # This logic for different models remains the same.
        # Ensure you've copied your full 'o4-mini' logic here if you use it.
        if model == "o4-mini":
            # ... (Your logic for o4-mini)
            st.warning("o4-mini logic not fully implemented in this example. Using standard chat completion.")

        # Logic for gpt-4o and other chat models
        user_content = [{"type": "text", "text": f"Generate questions in {selected_language}. {prompt}"}]
        if images:
            for image in images:
                base64_image = process_image(image)
                user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "low"}})
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=4096,
            temperature=0.6
        )
        if response.usage:
            st.info(f"📊 Token Usage: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}")
        
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"Fehler bei der Kommunikation mit der OpenAI API: {e}")
        logging.error(f"Fehler bei der OpenAI API: {e}")
        return None