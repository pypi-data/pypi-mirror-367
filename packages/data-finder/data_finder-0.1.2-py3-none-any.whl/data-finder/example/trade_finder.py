from datafinder.typed_attributes import *
from datafinder import QueryRunnerBase, DataFrame
from account_finder import AccountRelatedFinder


class TradeFinder:
    __table = 'trades'

    __symbol = StringAttribute('sym', 'VARCHAR', 'trades')
    __price = FloatAttribute('price', 'DOUBLE', 'trades')
    __account = AccountRelatedFinder(Attribute('account_id', 'INT', 'trades'),Attribute('id', 'INT', 'account_master'))

    @staticmethod
    def symbol() -> StringAttribute:
        return TradeFinder.__symbol

    @staticmethod
    def price() -> FloatAttribute:
        return TradeFinder.__price

    @staticmethod
    def account() -> AccountRelatedFinder:
        return TradeFinder.__account

    @staticmethod
    def find_all(date_from: datetime.date, date_to: datetime.date, as_of: str,
                 display_columns: list[Attribute],
                 filter_op: Operation = NoOperation()) -> DataFrame:
        return QueryRunnerBase.get_runner().select(display_columns, TradeFinder.__table, filter_op)


class TradeRelatedFinder:
    def __init__(self, source: Attribute, target: Attribute):
        join = JoinOperation(source,target)
        self.__symbol = StringAttribute('sym', 'VARCHAR', 'trades', join)
        self.__price = FloatAttribute('price', 'DOUBLE', 'trades', join)
        self.__account = AccountRelatedFinder(Attribute('account_id', 'INT', 'trades'),Attribute('id', 'INT', 'account_master'))

    def symbol(self) -> StringAttribute:
        return self.__symbol

    def price(self) -> FloatAttribute:
        return self.__price

    def account(self) -> AccountRelatedFinder:
        return self.__account

