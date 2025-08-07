import psycopg2
from psycopg2.extensions import cursor
from .floatvector import register_vector_info


# TODO make globally False by default in 0.4.0
# note: register_adapter is always global
# TODO make arrays True by defalt in 0.4.0
def register_vector(conn_or_curs=None, globally=True, arrays=False):
    conn = conn_or_curs if hasattr(conn_or_curs, 'cursor') else conn_or_curs.connection
    cur = conn.cursor(cursor_factory=cursor)
    scope = None if globally else conn_or_curs

    # use to_regtype to get first matching type in search path
    cur.execute("SELECT typname, oid FROM pg_type WHERE typname IN ('floatvector', '_floatvector')")
    type_info = dict(cur.fetchall())

    if 'floatvector' not in type_info:
        raise psycopg2.ProgrammingError('floatvector type not found in the database')

    register_vector_info(type_info['floatvector'], None, scope)