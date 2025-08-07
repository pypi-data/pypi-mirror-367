"""
币种配置
"""
from decimal import Decimal

from binance.utils import to_str


class CoinPriceLimit:
    """
    币种加个及限额
    """

    def __init__(self,
                 coin,
                 price,
                 min_limit,
                 max_limit,
                 std_usdt_min_amount,
                 std_usdt_max_amount) -> None:
        self.coin = coin
        self.price = price
        self.min_limit = min_limit
        self.max_limit = max_limit
        self.std_usdt_min_amount = std_usdt_min_amount
        self.std_usdt_max_amount = std_usdt_max_amount

    def __str__(self) -> str:
        return (f'coin: {self.coin}, price: {self.price}, '
                f'min_limit: {self.min_limit}, max_limit: {self.max_limit} \n')

    def __repr__(self) -> str:
        return self.__str__()

    def get_large_max_limit(self, large_limit: Decimal) -> Decimal:
        """
        计算更大的限额
        :param large_limit:
        :return:
        """
        return self.max_limit * large_limit / self.std_usdt_max_amount \
            if large_limit > self.std_usdt_max_amount else self.max_limit

    def get_specific_max_limit(self, specific_limit: Decimal) -> Decimal:
        """
        计算特定的限额
        :param specific_limit:
        :return:
        """
        return self.max_limit * specific_limit / self.std_usdt_max_amount

    def min_limit_str(self):
        """
        避免展示为科学记数法
        :return: min limit str
        """
        return to_str(self.min_limit)

    def max_limit_str(self):
        """
        避免展示为科学记数法
        :return: max limit str
        """
        return to_str(self.max_limit)
