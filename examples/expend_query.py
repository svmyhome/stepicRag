def expand_query(query: str) -> list[str]:
    if len(query.split()) <= 3:
        return [
            query,
            f"Что такое '{query}'?",
            f"Как использовать {query}?",
            f"Где найти документацию по {query}?"
        ]
    return [query]