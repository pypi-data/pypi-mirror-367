from sqlalchemy.dialects.postgresql import array
from sqlalchemy.sql.functions import GenericFunction
from sqlalchemy.types import Float, ARRAY, Integer, Boolean

from .floatvector import FLOATVECTOR


class floatvector_combine(GenericFunction):
    """
    这个函数用于将两个 double precision 类型的数组逐元素相加成一个新的向量返回这个新向量
    """
    type = ARRAY(Float)
    inherit_cache = True 
    name = "floatvector_combine"


class floatvector_accum(GenericFunction):
    """
    这个函数用于将一个向量累加到数组中，返回一个新的数组。
    其中，被累加的数组及结果数组的第一个元素为累加次数，之后的元素为各维度的累积值
    """
    type = ARRAY(Float)
    inherit_cache = True 
    name = "floatvector_accum"


class floatvector_cmp(GenericFunction):
    """
    这个函数逐个比较两个向量的元素，找到第一个不同的元素并根据它决定大小关系。
    如果第一个向量小于第二个，返回 -1；如果相等，返回 0；如果第一个向量大于第二个，返回 1。
    """
    type = Integer()
    inherit_cache = True 
    name = "floatvector_cmp"


class floatvector_gt(GenericFunction):
    """
    这个函数逐个比较两个向量的元素，找到第一个不同的元素并根据它决定大小关系。
    如果第一个向量大于第二个向量，则返回 true，否则返回 false
    """
    type = Boolean()
    inherit_cache = True 
    name = "floatvector_gt"


class floatvector_ge(GenericFunction):
    """
    这个函数逐个比较两个向量的元素，找到第一个不同的元素并根据它决定大小关系。
    如果第一个向量大于等于第二个向量，则返回 true，否则返回 false。
    """
    type = Boolean()
    inherit_cache = True 
    name = "floatvector_ge"


class floatvector_ne(GenericFunction):
    """
    这个函数用于比较两个向量，如果两个向量的任意元素不相等，则返回 true，否则返回 false。
    """
    type = Boolean()
    inherit_cache = True 
    name = "floatvector_ne"


class floatvector_eq(GenericFunction):
    """
    这个函数用于比较两个向量，如果两个向量的所有元素都相等，则返回 true，否则返回 false。
    """
    type = Boolean()
    inherit_cache = True 
    name = "floatvector_eq"


class floatvector_le(GenericFunction):
    """
    这个函数逐个比较两个向量的元素，找到第一个不同的元素并根据它决定大小关系。
    如果第一个向量小于等于第二个向量，则返回 true，否则返回 false。
    """
    type = Boolean()
    inherit_cache = True
    name = "floatvector_le"


class floatvector_lt(GenericFunction):
    """
    这个函数逐个比较两个向量的元素，找到第一个不同的元素并根据它决定大小关系。
    如果第一个向量小于于第二个向量，则返回 true，否则返回 false。
    """
    type = Boolean()
    inherit_cache = True
    name = "floatvector_lt"


class floatvector_spherical_distance(GenericFunction):
    """
    这个函数用于计算两个向量之间的球面距离（spherical distance），即两个向量之间的夹角的余弦值。
    """
    type = Float()
    inherit_cache = True
    name = "floatvector_spherical_distance"


class floatvector_negative_inner_product(GenericFunction):
    """
    这个函数用于计算两个向量的负内积（negative inner product），即两个向量对应位置上的元素相乘后求和并取负值。
    """
    type = Float()
    inherit_cache = True
    name = "floatvector_negative_inner_product"


class floatvector_l2_squared_distance(GenericFunction):
    """
    这个函数用于计算两个向量之间的 L2 范数的平方距离。
    L2 范数距离是向量元素差的平方和。
    """
    type = Float()
    inherit_cache = True
    name = "floatvector_l2_squared_distance"


class floatvector_avg(GenericFunction):
    """
    这个函数用于计算一个 double precision 类型数组中所有元素的值进行 N等分。
    N 是数组的第一个元素，并返回一个 N 等分后的向量。
    """
    type = FLOATVECTOR()
    inherit_cache = True
    name = "floatvector_avg"


class floatvector_sub(GenericFunction):
    """
    这个函数用于计算两个向量的元素级相减，返回一个新的向量，其中每个元素是对应位置上两个向量元素的差。
    """
    type = FLOATVECTOR()
    inherit_cache = True
    name = "floatvector_sub"


class floatvector_add(GenericFunction):
    """
    这个函数用于计算两个向量的元素级相加，返回一个新的向量，其中每个元素是对应位置上两个向量元素的和。
    """
    type = FLOATVECTOR()
    inherit_cache = True
    name = "floatvector_add"


class floatvector_norm(GenericFunction):
    """
    这个函数用于计算给定向量的范数，即向量元素的平方和的平方根。
    """
    type = Float()
    inherit_cache = True
    name = "floatvector_norm"


class floatvector_dims(GenericFunction):
    """
    这个函数用于返回给定向量的维度（即向量中元素的数量）。
    """
    type = Integer()
    inherit_cache = True
    name = "floatvector_dims"


class l2_distance(GenericFunction):
    """
    这个函数用于计算两个向量之间的 L2 范数距离。
    L2 范数距离也称为欧氏距离，表示两个向量之间的直线距离。
    """
    type = Float()
    inherit_cache = True
    name = "l2_distance"


class inner_product(GenericFunction):
    """
    这个函数用于计算两个向量的内积。
    内积是两个向量对应元素乘积的和。
    """
    type = Float()
    inherit_cache = True
    name = "inner_product"


class cosine_distance(GenericFunction):
    """
    这个函数用于计算两个向量之间的余弦距离。
    余弦距离是通过计算两个向量之间的夹角余弦值来衡量它们之间的相似度。
    """
    type = Float()
    inherit_cache = True
    name = "cosine_distance"