"""
decimal util
"""
from decimal import Decimal


def to_str(num: Decimal) -> str:
    """
    decimal to str
    :param num: decimal
    :return: str
    """
    return format(num, 'f')
