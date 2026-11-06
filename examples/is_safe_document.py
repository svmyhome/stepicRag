corrupted = ['игнорируй', 'забудь',
             'system prompt', 'выведи все', 'раскрой секрет']


def is_safe_document(document_text: str) -> bool:
    for word in corrupted:
        if word.lower() in document_text.lower():
            return False
    return True


print(is_safe_document('chdbhcd system prompt cdscdc'))


def validate_answer(answer: str, expected_keywords: list[str]) -> bool:
    for word in expected_keywords:
        if word.lower() in answer.lower():
            return True
    return False
