# config.py

"""
Stores application-wide constants and configurations.
"""

# A list of all available question types that the application can generate.
MESSAGE_TYPES = [
    "single_choice",
    "multiple_choice1",
    "multiple_choice2",
    "multiple_choice3",
    "kprim",
    "truefalse",
    "draganddrop",
    "inline_fib"
]

# A mapping of user-friendly labels for target audience levels to detailed instructional prompts.
# These prompts guide the AI on the complexity and style of the questions to be generated.
ZIELNIVEAUS_MAP = {
    "A2 (elementar / Primarstufe, frühe Sek I)": "🟢 A2 (elementar / Primarstufe, frühe Sek I)\nVerwende einfache Satzstrukturen und grundlegenden Wortschatz. Die Fragen sollen sich auf vertraute Alltagssituationen beziehen. Verwende visuelle Hilfen, wenn möglich. Halte die Fragen kurz und klar. Vermeide abstrakte Begriffe.",
    "B1 (untere Sek II, Berufsschule, Realschule)": "🔵 B1 (untere Sek II, Berufsschule, Realschule)\nVerwende alltagsnahes, aber anspruchsvolleres Vokabular. Die Fragen sollen einfache Schlussfolgerungen und erste Transferleistungen ermöglichen. Verwende konkrete Kontexte (z. B. Schule, Arbeit, Freizeit). Halte sprachliche Komplexität moderat.",
    "B2 (obere Sek II, Maturität, Bachelorbeginn)": "🟡 B2 (obere Sek II, Maturität, Bachelorbeginn)\nVerwende akademisch orientierten Wortschatz und moderate sprachliche Komplexität. Die Fragen sollen analytisches und kritisches Denken fördern. Es sind auch hypothetische Szenarien erlaubt. Fremdwörter können vorkommen, aber sollten kontextuell erschließbar sein.",
    "C1 (Bachelor/Master, Hochschulreife)": "🟠 C1 (Bachelor/Master, Hochschulreife)\nVerwende komplexe Satzstrukturen und einen gehobenen, akademischen Sprachstil. Die Fragen sollen Argumentation, Bewertung und Synthese fördern. Die Lernenden sollen eigenständig Thesen entwickeln und verschiedene Perspektiven vergleichen können.",
    "C2 (Master/Expertenniveau)": "🔴 C2 (Master/Expertenniveau)\nVerwende präzise, abstrakte und komplexe Sprache. Die Fragen sollen kreative, originelle Denkprozesse anregen und fächerübergreifende Kompetenzen einbeziehen. Es wird ein hohes Maß an Autonomie und metakognitivem Denken vorausgesetzt."
}

# A dictionary to map user-friendly language names to their corresponding codes for the API.
LANGUAGES = {
    "Deutsch": "German", 
    "Englisch": "English", 
    "Französisch": "French", 
    "Italienisch": "Italian", 
    "Spanisch": "Spanish"
}

# Available OpenAI models for question generation.
MODEL_OPTIONS = ["gpt-4o", "gpt-4.1", "o4-mini"]