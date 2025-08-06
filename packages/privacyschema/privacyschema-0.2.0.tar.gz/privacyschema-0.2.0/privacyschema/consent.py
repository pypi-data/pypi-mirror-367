"""
consent.py - Consent management logic
"""

# In-memory consent store (for demonstration purposes)
consent_store = {}

def register_consent(user_id, consent_data):
    """
    Register user consent.
    :param user_id: str
    :param consent_data: dict
    """
    consent_store[user_id] = {**consent_data, 'revoked': False}

def update_consent(user_id, consent_data):
    """
    Update user consent.
    :param user_id: str
    :param consent_data: dict
    """
    if user_id in consent_store:
        consent_store[user_id].update(consent_data)

def revoke_consent(user_id):
    """
    Revoke user consent.
    :param user_id: str
    """
    if user_id in consent_store:
        consent_store[user_id]['revoked'] = True

def is_consent_active(user_id):
    """
    Check if user consent is active.
    :param user_id: str
    :return: bool
    """
    return user_id in consent_store and not consent_store[user_id]['revoked']