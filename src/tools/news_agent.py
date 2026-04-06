
def summarize_news(articles, max_points=5):
    combined = "".join([
        f"""
HeadLines: {a.get('headline', '')}
Source Link: {a.get('source', '')}
Published: {a.get('published', '')}
Content: {a.get('summary', '')}
"""
        for a in articles
    ])

    return combined