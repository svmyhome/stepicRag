import hashlib


def mock_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def is_chunk_outdated(current_text: str, stored_text: str) -> bool:
    return mock_hash(stored_text) != mock_hash(current_text)


print(is_chunk_outdated('привет', 'Привет'))