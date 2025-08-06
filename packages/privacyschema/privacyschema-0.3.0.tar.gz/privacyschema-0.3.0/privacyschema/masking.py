"""
masking.py - Masking logic for personal data
"""
import re

def mask(data_type, value):
    """
    Mask a sensitive value (e.g., CPF, email, phone, RG, CNPJ, name, address) according to type.
    :param data_type: str - The type of data to mask (e.g., 'cpf', 'email', 'phone', 'rg', 'cnpj', 'name', 'address').
    :param value: str - The value to be masked.
    :return: str - The masked value.
    """
    if data_type == 'cpf':
        # Mask all but the last 2 digits
        return re.sub(r'\d(?=\d{2})', '*', value)
    if data_type == 'email':
        # Mask all but the first and last character before @
        user, domain = value.split('@')
        if len(user) <= 2:
            return '*@' + domain
        return user[0] + '*' * (len(user) - 2) + user[-1] + '@' + domain
    if data_type == 'phone':
        # Mask all but the last 2 digits
        return re.sub(r'\d(?=\d{2})', '*', value)
    if data_type == 'rg':
        # Mask all but the last 2 digits
        return re.sub(r'\d(?=\d{2})', '*', value)
    if data_type == 'cnpj':
        # Mask all but the last 4 digits
        return re.sub(r'\d(?=\d{4})', '*', value)
    if data_type == 'name':
        # Mask all but the first and last character of each word
        return ' '.join([
            w[0] + '*' * (len(w) - 2) + w[-1] if len(w) > 2 else w[0] + '*' for w in value.split()
        ])
    if data_type == 'address':
        # Mask all but the first and last character of each word, except for numbers
        def mask_word(w):
            if w.isdigit():
                return w
            if len(w) <= 2:
                return w[0] + '*'
            return w[0] + '*' * (len(w) - 2) + w[-1]
        return ' '.join([mask_word(w) for w in value.split()])
    return value