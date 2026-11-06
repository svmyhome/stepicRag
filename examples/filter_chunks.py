def filter_chunks_by_user(user_team: str, user_version: str, chunks: list[dict]) -> list[dict]:
    result = []
    for chunk in chunks:
        if chunk.get("team") == user_team and chunk.get("version") == user_version:
            result.append(chunk)
    return result



s = [{'k1':'qaz','team': 'user', 'sensitivity': 'internal', 'version': '2.4'},
     {'k2':'wsx','team': 'backend', 'sensitivity': 'internal', 'version': '2.4'},
     {'k3':'edc','team': 'user', 'sensitivity': 'internal', 'version': '2.3'}]

print(filter_chunks_by_user('user', '2.4', s))