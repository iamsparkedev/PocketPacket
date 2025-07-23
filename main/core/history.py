# history.py
# Handles request history for PocketPacket

# For MVP, this is a stub. You can expand with file/database storage later.

_history = []

def add_to_history(entry):
    """Add a request/response entry to history."""
    _history.append(entry)

def get_history():
    """Return the list of history entries."""
    return list(_history)
