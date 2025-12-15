from src.core.llm import PerplexityLLM

def summarize_news(articles, max_points=7):
    """
    Summarize a list of articles into numbered key points.
    """
    llm = PerplexityLLM()

    combined_text = "\n".join([f"{a['title']}: {a.get('snippet','')}" for a in articles])
    
    prompt = f"""
    Summarize the following news articles into {max_points} concise key points:

    {combined_text}

    Format the output as numbered points.
    """
    
    response = llm.invoke(prompt)
    return response  
