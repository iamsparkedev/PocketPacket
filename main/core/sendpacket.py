# sendpacket.py
# Handles sending HTTP requests for PocketPacket

import requests

def send_packet(url, method, headers, body):
    """
    Sends an HTTP request using the requests library.
    Returns status, headers, body.
    """
    try:
        response = requests.request(method, url, headers=headers, data=body)
        return response.status_code, dict(response.headers), response.text
    except Exception as e:
        return None, None, str(e)
