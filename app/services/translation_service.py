import os
import time
import logging
import requests

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

logger = logging.getLogger(__name__)

DetectorFactory.seed = 0

API_URL = "https://api.mymemory.translated.net/get"

MYMEMORY_EMAIL = os.getenv("MYMEMORY_EMAIL")

class TranslationError(Exception):
    pass
def split_text(text, max_bytes=450):
    chunks = []
    current_chunk = ""

    for char in text:
        if len((current_chunk + char).encode("utf-8")) > max_bytes:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = char
        else:
            current_chunk += char

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def translate_chunk(text, source_language):
    params = {
        "q": text,
        "langpair": f"{source_language}|en",
        "mt": 1
    }

    if MYMEMORY_EMAIL:
        params["de"] = MYMEMORY_EMAIL

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()
        if data.get("responseStatus") != 200:
            raise TranslationError(
                data.get(
                    "responseDetails",
                    "Translation failed"
                )
            )

        translated = data["responseData"]["translatedText"]

        if not translated:
            raise TranslationError(
                "Empty translation result"
            )

        return translated

    except requests.RequestException as e:
        logger.error(
            f"MyMemory request failed: {e}"
        )

        raise TranslationError(
            "Translation API is unavailable"
        ) from e


def translate_to_english(text):
    if not text or not text.strip():
        raise TranslationError(
            "Journal content cannot be empty"
        )

    try:
        source_language = detect(text)

        logger.info(
            f"Detected journal language: {source_language}"
        )

    except LangDetectException as e:
        raise TranslationError(
            "Unable to detect journal language"
        ) from e

    if source_language == "en":
        return text

    chunks = split_text(text)

    translated_chunks = []

    for index, chunk in enumerate(chunks):
        logger.info(
            f"Translating chunk {index + 1}/{len(chunks)}"
        )
        translated = translate_chunk(
            chunk,
            source_language
        )

        translated_chunks.append(translated)

        if index < len(chunks) - 1:
            time.sleep(0.5)

    translated_text = " ".join(
        translated_chunks
    )

    return translated_text