"""
validation.py - Validation logic for personal data
"""
import re

def validate(data):
    """
    Validate if the given data contains valid personal information.
    Currently supports CPF and email validation.
    :param data: dict - The user data to validate.
    :return: dict - Validation results for each field.
    """
    result = {}
    if 'cpf' in data:
        result['cpf'] = is_valid_cpf(data['cpf'])
    if 'email' in data:
        result['email'] = is_valid_email(data['email'])
    # Add more validations as needed
    return result

def is_valid_cpf(cpf):
    """
    Validate CPF (Brazilian ID).
    :param cpf: str
    :return: bool
    """
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    d1 = ((sum1 * 10) % 11) % 10
    sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    d2 = ((sum2 * 10) % 11) % 10
    return d1 == int(cpf[9]) and d2 == int(cpf[10])

def is_valid_email(email):
    """
    Validate email address.
    :param email: str
    :return: bool
    """
    return re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email) is not None