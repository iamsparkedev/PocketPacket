# Format response output for display
import json
def format_response(resp_text):
    """
    Try to pretty-print JSON, else return raw text.
    """
    try:
        parsed = json.loads(resp_text)
        return json.dumps(parsed, indent=2)
    except Exception:
        return resp_text

def format_headers(headers_dict):
    """
    Format headers dict for display.
    """
    if not headers_dict:
        return ""
    return '\n'.join([f"{k}: {v}" for k, v in headers_dict.items()])
# utils.py
# Utility functions for PocketPacket

import ast
import json

def parse_headers(headers_str):
    """
    Safely parse headers from a string to a dictionary.
    Accepts Python dict or JSON formats.
    Args:
        headers_str (str): String representation of headers (Python dict or JSON).
    Returns:
        dict: Parsed headers dictionary.
    Raises:
        ValueError: If parsing fails.
    """
    if not headers_str.strip():
        return {}
    try:
        # Try parsing as Python dict
        return ast.literal_eval(headers_str)
    except Exception:
        try:
            # Try parsing as JSON
            return json.loads(headers_str)
        except Exception:
            raise ValueError("Headers must be a valid Python dictionary or JSON object (e.g., {'Content-Type': 'application/json'} or {\"Content-Type\": \"application/json\"})")
