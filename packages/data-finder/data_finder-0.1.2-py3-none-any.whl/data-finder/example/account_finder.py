from datafinder.typed_attributes import *
from datafinder import QueryRunnerBase, DataFrame


class AccountFinder:
    __table = 'account_master'

    __id = IntegerAttribute('id', 'INT', 'account_master')
    __name = StringAttribute('name', 'VARCHAR', 'account_master')

    @staticmethod
    def id() -> IntegerAttribute:
        return AccountFinder.__id

    @staticmethod
    def name() -> StringAttribute:
        return AccountFinder.__name

    @staticmethod
    def find_all(date_from: datetime.date, date_to: datetime.date, as_of: str,
                 display_columns: list[Attribute],
                 filter_op: Operation = NoOperation()) -> DataFrame:
        return QueryRunnerBase.get_runner().select(display_columns, AccountFinder.__table, filter_op)


class AccountRelatedFinder:
    def __init__(self, source: Attribute, target: Attribute):
        join = JoinOperation(source,target)
        self.__id = IntegerAttribute('id', 'INT', 'account_master', join)
        self.__name = StringAttribute('name', 'VARCHAR', 'account_master', join)

    def id(self) -> IntegerAttribute:
        return self.__id

    def name(self) -> StringAttribute:
        return self.__name

