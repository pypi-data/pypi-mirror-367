import pytest
from vexdb.sqlalchemy import *
import numpy as np
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import create_engine, insert, inspect, select, MetaData, Table, Column, Index, Integer
from sqlalchemy.exc import StatementError
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import declarative_base, Session

try:
    from sqlalchemy.orm import mapped_column
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    sqlalchemy_version = 2
except ImportError:
    mapped_column = Column
    sqlalchemy_version = 1

engine = create_engine('postgresql+psycopg2://test:Test%401234@localhost:5432/postgres')


class TestFunction:
    def test_floatvector_combind(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_combine([1.0,2.0,3.0], [4,5,6])))
             assert [v for v in items] == [5.0, 7.0, 9.0]

    def test_floatvector_accum(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_accum([1.0,2.0,3.0], [4,5])))
             assert [v for v in items] == [2.0, 6.0, 8.0]

    def test_floatvector_cmp(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_cmp([1,1,1,1], [2,2,2,2])))
             assert items == -1

    def test_floatvector_gt(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_gt([1,1,1,1], [2,2,2,2])))
             assert items == False

    def test_floatvector_ge(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_ge([1,1,1,1], [2,2,2,2])))
             assert items == False

    def test_floatvector_ne(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_ne([1,1,1,1], [2,2,2,2])))
             assert items == True

    def test_floatvector_eq(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_eq([1,1,1,1], [2,2,2,2])))
             assert items == False

    def test_floatvector_le(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_le([1,1,1,1], [2,2,2,2])))
             assert items == True

    def test_floatvector_lt(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_lt([1,1,1,1], [2,2,2,2])))
             assert items == True

    def test_floatvector_spherical_distance(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_spherical_distance([1,1,1,1], [2,2,2,2])))
             assert items == 0.0

    def test_floatvector_negative_inner_product(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_negative_inner_product([1,1,1,1], [2,2,2,2])))
             assert items == -8.0

    def test_floatvector_l2_squared_distance(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_l2_squared_distance([1,1,1,1], [2,2,2,2])))
             assert items == 4.0

    def test_floatvector_avg(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_avg([3,4.56,7.89])))
             print(f'type:{type(items)}, value:{items}')
             assert [v for v in items] == pytest.approx([1.52,2.63], abs=1e-6)

    def test_floatvector_sub(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_sub([1,1,1,1], [2,2,2,2])))
             assert [v for v in items] == [-1,-1,-1,-1]

    def test_floatvector_add(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_add([1,1,1,1], [2,2,2,2])))
             assert [v for v in items] == [3,3,3,3]

    def test_floatvector_norm(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_norm([1,1,1,1])))
             assert items == 2.0

    def test_floatvector_dims(self):
        with Session(engine) as session:
             items = session.scalar(select(floatvector_dims([1,1,1,1])))
             assert items == 4

    def test_l2_distance(self):
        with Session(engine) as session:
             items = session.scalar(select(l2_distance([1,1,1,1], [2,2,2,2])))
             assert items == 2.0

    def test_inner_product(self):
        with Session(engine) as session:
             items = session.scalar(select(inner_product([1, 1, 1, 1], [2, 2, 2, 2])))
             assert items == 8.0

    def test_cosine_distance(self):
        with Session(engine) as session:
             items = session.scalar(select(cosine_distance([1, 1, 1, 1], [2, 2, 2, 2])))
             assert items == 0.0

