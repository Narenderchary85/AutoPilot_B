from src.core.llm import PerplexityLLM

def summarize_news(articles, max_points=7):
    llm = PerplexityLLM()

    text = "\n".join(
        f"- {a['title']}: {a['snippet']}"
        for a in articles
    )

    system_prompt = "You are a professional news editor."
    user_prompt = f"""
Summarize the following news into {max_points} concise bullet points.
Avoid repeating headlines verbatim.

{text}
"""

    response = llm.generate(system_prompt, user_prompt)
    return response["choices"][0]["message"]["content"]

