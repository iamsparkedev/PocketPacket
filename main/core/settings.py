# settings.py
# Handles settings for PocketPacket (stub for future expansion)

_settings = {}

def get_setting(key, default=None):
    return _settings.get(key, default)

def set_setting(key, value):
    _settings[key] = value
