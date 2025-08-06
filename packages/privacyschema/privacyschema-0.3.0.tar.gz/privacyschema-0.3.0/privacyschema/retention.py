"""
retention.py - Retention policy logic
"""
from datetime import datetime

# In-memory retention store (for demonstration purposes)
retention_store = {}

def mark_for_expiration(user_id, expiration_date):
    """
    Mark data for expiration/removal.
    :param user_id: str
    :param expiration_date: datetime
    """
    retention_store[user_id] = {'expiration_date': expiration_date}

def is_expired(user_id):
    """
    Check if data is expired.
    :param user_id: str
    :return: bool
    """
    if user_id not in retention_store:
        return False
    return datetime.now() > retention_store[user_id]['expiration_date']