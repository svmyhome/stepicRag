def is_production_ready(config: dict) -> bool:
    required_flags = (
        "logging_enabled",
        "has_timeouts",
        "input_sanitized",
        "tools_safe",
        "has_fallback",
    )
    return all(config.get(flag) is True for flag in required_flags)


def is_safe_filename(filename: str) -> bool:
    if not filename.endswith(".md"):
        return False
    name = filename[:-3]  # проверяем имя отдельно от расширения .md
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-_"
    return bool(name) and all(char in allowed for char in name)
