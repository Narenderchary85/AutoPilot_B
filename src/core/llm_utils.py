def extract_text(response: dict) -> str:
    """
    Extract text from Gemini/OpenAI/Perplexity/Ollama responses safely
    """

    # Gemini
    if "candidates" in response:
        return response["candidates"][0]["content"]["parts"][0]["text"].strip()

    # OpenAI / Grok / Perplexity
    if "choices" in response:
        return response["choices"][0]["message"]["content"].strip()

    # Ollama
    if "message" in response:
        return response["message"]["content"].strip()

    raise ValueError(f"Unknown LLM response format: {response}")