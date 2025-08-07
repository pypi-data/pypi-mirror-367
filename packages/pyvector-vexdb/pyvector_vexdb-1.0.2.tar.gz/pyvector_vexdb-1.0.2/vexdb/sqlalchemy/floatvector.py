import json
from sqlalchemy.dialects.postgresql.base import ischema_names
from sqlalchemy.types import UserDefinedType, Float, String
from ..utils import Vector

class FLOATVECTOR(UserDefinedType):
    """
    自定义FloatVector类型
    """
    cache_ok = True
    _string = String()

    def __init__(self, dim=None):
        super(UserDefinedType, self).__init__()
        self.dim = dim

    def get_col_spec(self, **kv):
        """
        定义数据库中类型名称
        :param kv:
        :return:
        """
        if self.dim is None:
            return 'FLOATVECTOR'
        return 'FLOATVECTOR(%d)' % self.dim

    def bind_processor(self, dialect):
        """
        在插入或者更新时，将数组转换为 JSON 格式
        :param dialect:
        :return:
        """
        def process(value):
            return Vector._to_db(value, self.dim)
        return process

    def literal_processor(self, dialect):
        """
        处理字面量
        :param dialect:
        :return:
        """
        string_literal_processor = self._string._cached_literal_processor(dialect)

        def process(value):
            return string_literal_processor(Vector._to_db(value, self.dim))

        return process

    def result_processor(self, dialect, coltype):
        """
        将查询结果转为数组
        :param dialect:
        :param coltype:
        :return:
        """
        def process(value):
            return Vector._from_db(value)
        return process

    class comparator_factory(UserDefinedType.Comparator):
        def l2_distance(self, other):
            return self.op('<->', return_type=Float)(other)

        def negative_inner_product(self, other):
            return self.op('<#>', return_type=Float)(other)

        def cosine_distance(self, other):
            return self.op('<=>', return_type=Float)(other)

        def add(self, other):
            return self.op('+', return_type=Float)(other)

        def sub(self, other):
            return self.op('-', return_type=Float)(other)

# for reflection
ischema_names['floatvector'] = FLOATVECTOR