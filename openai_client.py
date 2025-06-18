# openai_client.py

"""
Manages the OpenAI client and API calls.
"""

import streamlit as st
import logging
import httpx
from openai import OpenAI
from utils import process_image

def initialize_client(api_key):
    """Initializes and returns the OpenAI client."""
    if not api_key:
        return None
    try:
        # Clear proxy settings to avoid connection issues
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
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
    Du bist ein Experte im Bildungsbereich... (Your full system prompt here)
    # Zielniveaus
    [ZIELNIVEAU_INJECTION]
    ... (Rest of your system prompt)
    """
    system_prompt = system_prompt_template.replace("[ZIELNIVEAU_INJECTION]", selected_zielniveau)

    try:
        if model == "o4-mini":
            # o4-mini specific logic...
            # This part remains the same as in your original script.
            pass  # Placeholder for your o4-mini logic
        else:
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
            # Token usage and caching info display logic remains the same
            if response.usage:
                st.info(f"📊 Token Usage: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}")
            
            return response.choices[0].message.content

    except Exception as e:
        st.error(f"Fehler bei der Kommunikation mit der OpenAI API: {e}")
        logging.error(f"Fehler bei der OpenAI API: {e}")
        return None