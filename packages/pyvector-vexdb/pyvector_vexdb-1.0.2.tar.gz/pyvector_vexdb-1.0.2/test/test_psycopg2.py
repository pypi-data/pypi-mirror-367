import numpy as np
from vexdb.psycopg2 import register_vector
import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor, NamedTupleCursor
from psycopg2.pool import ThreadedConnectionPool

# 使用dsn
conn = psycopg2.connect("dbname=postgres user=test password=Test@1234 host=localhost port=5432")
# 使用关键字
# conn = psycopg2.connect(
#     dbname="postgres",
#     user="test",
#     password="Test@1234",
#     host="localhost",
#     port=5432)
conn.autocommit = True

cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS psycopg2_items')
cur.execute('CREATE TABLE psycopg2_items (id bigserial PRIMARY KEY, embedding floatvector(3))')

# 注册到连接
register_vector(conn)
# 注册到游标
# register_vector(cur)


class TestPsycopg2:
    def setup_method(self, test_method):
        cur.execute('DELETE FROM psycopg2_items')

    def test_vector(self):
        embedding = np.array([1.5, 2, 3])
        cur.execute('INSERT INTO psycopg2_items (embedding) VALUES (%s), (NULL)', (embedding,))

        cur.execute('SELECT embedding FROM psycopg2_items ORDER BY id')
        res = cur.fetchall()
        assert np.array_equal(res[0][0], embedding)
        assert res[0][0].dtype == np.float32
        assert res[1][0] is None

    def test_query(self):
        pass

    def test_cursor_factory(self):
        for cursor_factory in [DictCursor, RealDictCursor, NamedTupleCursor]:
            conn = psycopg2.connect(host='localhost', port=5432, database='postgres', user='test', password='Test@1234')
            cur = conn.cursor(cursor_factory=cursor_factory)
            register_vector(cur, globally=False)
            conn.close()

    def test_cursor_factory_connection(self):
        for cursor_factory in [DictCursor, RealDictCursor, NamedTupleCursor]:
            conn = psycopg2.connect(host='localhost', port=5432, database='postgres', user='test', password='Test@1234', cursor_factory=cursor_factory)
            register_vector(conn, globally=False)
            conn.close()

    def test_pool(self):
        pool = ThreadedConnectionPool(1, 1, host='localhost', port=5432, database='postgres', user='test', password='Test@1234')

        conn = pool.getconn()
        try:
            # use globally=True for apps to ensure registered with all connections
            register_vector(conn, globally=False)
        finally:
            pool.putconn(conn)

        conn = pool.getconn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT '[1,2,3]'::floatvector")
            res = cur.fetchone()
            assert np.array_equal(res[0], np.array([1, 2, 3]))
        finally:
            pool.putconn(conn)

        pool.closeall()


