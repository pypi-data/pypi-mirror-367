"""
audit.py - Audit logging for sensitive data operations
"""
from datetime import datetime

# In-memory audit log (for demonstration purposes)
audit_log = []

def log_operation(user_id, operation, details):
    """
    Log an operation on sensitive data.
    :param user_id: str
    :param operation: str
    :param details: dict
    """
    audit_log.append({
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'operation': operation,
        'details': details
    })

def get_audit_logs():
    """
    Get all audit logs.
    :return: list
    """
    return audit_log