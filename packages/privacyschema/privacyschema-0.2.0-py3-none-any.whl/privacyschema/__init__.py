"""
PrivacySchema main module
"""

from .validation import validate, is_valid_cpf, is_valid_email
from .masking import mask
from .consent import register_consent, update_consent, revoke_consent, is_consent_active
from .retention import mark_for_expiration, is_expired
from .audit import log_operation, get_audit_logs

# Expose the main API
__all__ = [
    'validate', 'is_valid_cpf', 'is_valid_email',
    'mask',
    'register_consent', 'update_consent', 'revoke_consent', 'is_consent_active',
    'mark_for_expiration', 'is_expired',
    'log_operation', 'get_audit_logs'
]