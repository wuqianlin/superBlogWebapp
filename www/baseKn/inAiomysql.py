import asyncio, aiomysql, logging

@asyncio.coroutine
def create_pool(loop, **kw):
    print('create database connection pool...')
    global __pool
    __pool = yield from aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )
    print(loop)

@asyncio.coroutine
def select(sql, args, size=None):
    print("-----")
    global __pool
    with (yield from __pool) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)
        yield from cur.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = yield from cur.fetchmany(size)
        else:
            rs = yield from cur.fetchall()
        yield from cur.close()
        logging.info('rows returned: %s' % len(rs))
        print(rs)
        return rs

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete( create_pool(loop, user='root', password='xyzcn3!@#',db='awesome') )
    #loop.run_forever()
    loop.run_until_complete(select("select ? from users", '*',1).__next__())

