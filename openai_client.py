# openai_client.py

"""
Manages the OpenAI client and API calls, including special handling for o4-mini.
"""

import streamlit as st
import logging
import httpx
from openai import OpenAI
from utils import process_image
import os

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
    """Fetches a response from the OpenAI API, with custom logic for different models."""
    if not client:
        st.error("OpenAI-Client nicht initialisiert. Bitte geben Sie einen gültigen API-Schlüssel ein.")
        return None

    system_prompt_template = """
    Du bist ein Experte im Bildungsbereich, spezialisiert auf die Erstellung von Testfragen und -antworten...
    # Zielniveaus
    [ZIELNIVEAU_INJECTION]
    ... (rest of your system prompt) ...
    Achte stets darauf, dass die Formulierungen und kognitiven Anforderungen dem Niveau des vorgesehenen Lernendenkreises entsprechen.
    """
    system_prompt = system_prompt_template.replace("[ZIELNIVEAU_INJECTION]", selected_zielniveau)

    try:
        # --- START OF o4-mini IMPLEMENTATION ---
        if model == "o4-mini":
            st.info(f"🧠 Rufe OpenAI Reasoning API (o4-mini) mit '{reasoning_effort}' Aufwand auf...")
            
            # Construct the payload according to the client.responses.create format
            input_payload = []
            
            # 1. Add the developer role with system and user prompts
            full_text_prompt = f"Generate questions in {selected_language}.\n\n{system_prompt}\n\n{prompt}"
            input_payload.append({
                "role": "developer",
                "content": [{"type": "input_text", "text": full_text_prompt}]
            })

            # 2. Add the user role with images, if they exist
            if images:
                image_content = []
                for image in images:
                    base64_image = process_image(image)
                    image_content.append({
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}"
                    })
                input_payload.append({"role": "user", "content": image_content})

            # 3. Call the API
            response_obj = client.responses.create(
                model="o4-mini",
                input=input_payload,
                reasoning={"effort": reasoning_effort},
                text={"format": {"type": "text"}},
                tools=[],
                store=False
            )
            
            # 4. Parse the response
            # The response is a list of events. We need the last 'assistant' message.
            if hasattr(response_obj, 'output') and isinstance(response_obj.output, list):
                for item in reversed(response_obj.output): # Check from the end
                    if hasattr(item, 'role') and item.role == "assistant":
                        if hasattr(item, 'content') and item.content and isinstance(item.content, list):
                            # The text is in the first element of the content list
                            return item.content[0].text
            
            st.error("Konnte keine gültige Antwort vom o4-mini Modell finden.")
            logging.error(f"Unerwartete o4-mini Antwortstruktur: {response_obj}")
            return None
        # --- END OF o4-mini IMPLEMENTATION ---

        else: # Logic for gpt-4o and other standard chat models
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
                max_tokens=15000,
                temperature=0.4
            )
            if response.usage:
                st.info(f"📊 Token Usage: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}")
            
            return response.choices[0].message.content

    except Exception as e:
        st.error(f"Fehler bei der Kommunikation mit der OpenAI API: {e}")
        logging.error(f"Fehler bei der OpenAI API: {e}")
        return None