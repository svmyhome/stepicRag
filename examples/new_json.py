import json



def validate_llm_response(json_str: str) -> bool:
    try:
        json_obj = json.loads(json_str)
    except json.JSONDecodeError:
        return False

    if not isinstance(json_obj, dict) or "task_key" not in json_obj or "summary" not in json_obj:
        return False

    ts_key = json_obj["task_key"].split('-')
    if len(ts_key) != 2 or not ts_key[0].isalpha() or not ts_key[0].isupper() or not ts_key[1].isdigit():
        return False
    sum1 = json_obj["summary"]
    if not sum1  or len(sum1)> 60:
        return False
    return True

