import orm, sys
import asyncio
from models import User, Blog, Comment

@asyncio.coroutine
def test():
    yield from orm.create_pool(loop=loop, host='localhost', port=3306, user='root', password='123456', database='awesome')
    user = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
    #yield from user.save()
    r = yield from user.findAll()

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()
if loop.is_closed():
    sys.exit(0)




