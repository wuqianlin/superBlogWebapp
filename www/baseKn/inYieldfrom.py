def reader():
    for i in range(4):
        yield '<<%s' % i

def reader_wrapper(g):
    yield from g

wrap = reader_wrapper( reader() )
for i in wrap:
    print(i)

def writer():
    while True:
        w = (yield)
        print('>>', w)

def writer_wrapper(coro1):
    yield from coro1

