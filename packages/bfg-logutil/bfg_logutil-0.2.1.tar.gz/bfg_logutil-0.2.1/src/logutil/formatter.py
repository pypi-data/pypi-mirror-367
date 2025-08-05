import json
import re

allowed_chars = re.compile(r"^[a-zA-Z0-9_\-\.@]+$")
any_whitespace = re.compile(r"\s+")


def encode(val):
    if not isinstance(val, str):
        val = json.dumps(val, separators=(",", ":"))

    if allowed_chars.match(val):
        return val

    # replace whitespaces with a single space
    val = any_whitespace.sub(" ", val)

    has_double_quotes = '"' in val
    if not has_double_quotes:
        return f'"{val}"'

    has_single_quotes = "'" in val
    if not has_single_quotes:
        return f"'{val}'"

    # replace any double quotes with a single quote
    val = val.replace('"', "'")
    return f'"{val}"'


def format_params(params):
    if params is None:
        return ""
    return " ".join(f"{k}={encode(v)}" for k, v in params.items())
