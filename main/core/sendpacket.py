# sendpacket.py
# Handles sending HTTP requests for PocketPacket

import requests

def send_packet(url, method, headers, body):
    """
    Sends an HTTP request using the requests library.
    Args:
        url (str): The target URL.
        method (str): HTTP method (GET, POST, etc.).
        headers (dict): Request headers.
        body (str): Request body.
    Returns:
        tuple: (status_code, response_text) or (None, error_message)
    """
    try:
        response = requests.request(method, url, headers=headers, data=body)
        return response.status_code, response.text
    except Exception as e:
        return None, str(e)
