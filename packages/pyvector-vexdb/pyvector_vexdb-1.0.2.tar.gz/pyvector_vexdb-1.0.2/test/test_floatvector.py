import pytest
from vexdb.sqlalchemy import *
import numpy as np
from sqlalchemy import create_engine, insert, inspect, select, MetaData, Table, Column, Index, Integer
from sqlalchemy.exc import StatementError
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import declarative_base, Session
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from sqlalchemy.orm import mapped_column
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    sqlalchemy_version = 2
except ImportError:
    mapped_column = Column
    sqlalchemy_version = 1

engine = create_engine('postgresql+psycopg2://test:Test%401234@localhost:5432/postgres', echo=True)


Base = declarative_base()


class Item(Base):
    __tablename__ = 'sqlalchemy_orm_item'

    id = mapped_column(Integer, primary_key=True)
    embedding = mapped_column(FLOATVECTOR(3))

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

index = Index(
    'sqlalchemy_orm_index',
    Item.embedding,
    postgresql_using='hnsw',
    postgresql_with={'m': 16, 'ef_construction': 64},
    postgresql_ops={'embedding': 'floatvector_l2_ops'}
)
index.create(engine)


def create_items():
    session = Session(engine)
    session.add(Item(id=1, embedding=[1, 1, 1]))
    session.add(Item(id=2, embedding=[2, 2, 2]))
    session.add(Item(id=3, embedding=[1, 1, 2]))
    session.commit()

class TestFloatVector:
    def setup_method(self, test_method):
        with Session(engine) as session:
            session.query(Item).delete()
            session.commit()

    def test_core(self):
        metadata = MetaData()

        item_table = Table(
            'sqlalchemy_core_item',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('embedding', FLOATVECTOR(3))
        )

        metadata.drop_all(engine)
        metadata.create_all(engine)

        ivfflat_index = Index(
            'sqlalchemy_core_ivfflat_index',
            item_table.c.embedding,
            postgresql_using='ivfflat',
            postgresql_with={'ivf_nlist': 100},
            postgresql_ops={'embedding': 'floatvector_l2_ops'}
        )
        ivfflat_index.create(engine)

        hnsw_index = Index(
            'sqlalchemy_core_hnsw_index',
            item_table.c.embedding,
            postgresql_using='hnsw',
            postgresql_with={'m': 16, 'ef_construction': 64},
            postgresql_ops={'embedding': 'floatvector_l2_ops'}
        )
        hnsw_index.create(engine)

    def test_orm(self):
        item = Item(embedding=np.array([1.5, 2, 3]))
        item2 = Item(embedding=[4, 5, 6])
        item3 = Item()

        session = Session(engine)
        session.add(item)
        session.add(item2)
        session.add(item3)
        session.commit()

        stmt = select(Item)
        with Session(engine) as session:
            items = [v[0] for v in session.execute(stmt).all()]
            assert items[0].id == 1
            assert items[1].id == 2
            assert items[2].id == 3
            assert np.array_equal(items[0].embedding, np.array([1.5, 2, 3]))
            assert items[0].embedding.dtype == np.float32
            assert np.array_equal(items[1].embedding, np.array([4, 5, 6]))
            assert items[1].embedding.dtype == np.float32
            assert items[2].embedding is None

    def test_floatvector(self):
        session = Session(engine)
        session.add(Item(id=1, embedding=[1, 2, 3]))
        session.commit()
        item = session.get(Item, 1)
        assert item.embedding.tolist() == [1, 2, 3]

    def test_floatvector_l2_distance(self):
        create_items()
        with Session(engine) as session:
            items = session.query(Item).order_by(Item.embedding.l2_distance([1, 1, 1])).all()
            assert [v.id for v in items] == [1, 3, 2]

    def test_floatvector_l2_distance_orm(self):
        create_items()
        with Session(engine) as session:
            items = session.scalars(select(Item).order_by(Item.embedding.l2_distance([1, 1, 1])))
            assert [v.id for v in items] == [1, 3, 2]

    def test_floatvector_negative_inner_product(self):
        create_items()
        with Session(engine) as session:
            items = session.query(Item).order_by(Item.embedding.negative_inner_product([1, 1, 1])).all()
            assert [v.id for v in items] == [2, 3, 1]

    def test_floatvector_negative_inner_product_orm(self):
        create_items()
        with Session(engine) as session:
            items = session.scalars(select(Item).order_by(Item.embedding.negative_inner_product([1, 1, 1])))
            assert [v.id for v in items] == [2, 3, 1]

    def test_floatvector_cosine_distance(self):
        create_items()
        with Session(engine) as session:
            items = session.query(Item).order_by(Item.embedding.cosine_distance([1, 1, 1])).all()
            assert [v.id for v in items] == [1, 2, 3]

    def test_floatvector_cosine_distance_orm(self):
        create_items()
        with Session(engine) as session:
            items = session.scalars(select(Item).order_by(Item.embedding.cosine_distance([1, 1, 1])))
            assert [v.id for v in items] == [1, 2, 3]

    def test_filter(self):
        create_items()
        with Session(engine) as session:
            query = session.query(Item).filter(Item.embedding.l2_distance([1, 1, 1]) < 1)
            compiled_query = query.statement.compile()
            print(compiled_query)
            items = query.all()
            assert [v.id for v in items] == [1]

    def test_filter_orm(self):
        create_items()
        with Session(engine) as session:
            items = session.scalars(select(Item).filter(l2_distance(Item.embedding,[1, 1, 1]) < 1))
            assert [v.id for v in items] == [1]

    def test_select(self):
        with Session(engine) as session:
            session.add(Item(embedding=[2, 3, 3]))
            items = session.query(Item.embedding.l2_distance([1, 1, 1])).first()
            assert items[0] == 3

    def test_select_orm(self):
        with Session(engine) as session:
            session.add(Item(embedding=[2, 3, 3]))
            items = session.scalars(select(Item.embedding.l2_distance([1, 1, 1]))).all()
            assert items[0] == 3

    def test_bad_dimensions(self):
        item = Item(embedding=[1, 2])
        session = Session(engine)
        session.add(item)
        with pytest.raises(StatementError, match='expected 3 dimensions, not 2'):
            session.commit()

    def test_bad_ndim(self):
        item = Item(embedding=np.array([[1, 2, 3]]))
        session = Session(engine)
        session.add(item)
        with pytest.raises(StatementError, match='expected ndim to be 1'):
            session.commit()

    def test_bad_dtype(self):
        item = Item(embedding=np.array(['one', 'two', 'three']))
        session = Session(engine)
        session.add(item)
        with pytest.raises(StatementError, match='could not convert string to float'):
            session.commit()

    def test_inspect(self):
        columns = inspect(engine).get_columns('sqlalchemy_orm_item')
        assert isinstance(columns[1]['type'], FLOATVECTOR)

    def test_literal_binds(self):
        sql = select(Item).order_by(Item.embedding.l2_distance([1, 2, 3])).compile(engine, compile_kwargs={
            'literal_binds': True})
        assert "embedding <-> '[1.0,2.0,3.0]'" in str(sql)

    def test_insert(self):
        session = Session(engine)
        session.execute(insert(Item).values(embedding=np.array([1, 2, 3])))

    def test_insert_bulk(self):
        session = Session(engine)
        session.execute(insert(Item), [{'embedding': np.array([1, 2, 3])}])

    def test_automap(self):
        session = Session(engine)
        metadata = MetaData()
        metadata.reflect(engine, only=['sqlalchemy_orm_item'])
        AutoBase = automap_base(metadata=metadata)
        AutoBase.prepare()
        AutoItem = AutoBase.classes.sqlalchemy_orm_item
        session.execute(insert(AutoItem), [{'embedding': np.array([1, 2, 3])}])
        item = session.query(AutoItem).first()
        assert item.embedding.tolist() == [1, 2, 3]
