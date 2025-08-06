"""
masking.py - Masking logic for personal data
"""

def mask(data_type, value):
    """
    Mask a sensitive value (e.g., CPF, email) according to type.
    :param data_type: str - The type of data to mask (e.g., 'cpf', 'email').
    :param value: str - The value to be masked.
    :return: str - The masked value.
    """
    if data_type == 'cpf':
        # Mask all but the last 2 digits
        return '*' * (len(value) - 2) + value[-2:]
    if data_type == 'email':
        # Mask all but the first and last character before @
        user, domain = value.split('@')
        if len(user) <= 2:
            return '*@' + domain
        return user[0] + '*' * (len(user) - 2) + user[-1] + '@' + domain
    # TODO: Add more types (phone, etc.)
    return value