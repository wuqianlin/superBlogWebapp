'''***'''
'''
在学习异步IO模型前，我们先来了解协程。
协程，又称微线程，纤程。英文名Coroutine。
协程的概念很早就提出来了，但直到最近几年才在某些语言（如Lua）中得到广泛应用。
子程序，或者称为函数，在所有语言中都是层级调用，比如A调用B，B在执行过程中又调用了C，C执行完毕返回，B执行完毕返回，最后是A执行完毕。
所以子程序调用是通过栈实现的，一个线程就是执行一个子程序。
子程序调用总是一个入口，一次返回，调用顺序是明确的。而协程的调用和子程序不同。
协程看上去也是子程序，但执行过程中，在子程序内部可中断，然后转而执行别的子程序，在适当的时候再返回来接着执行。
注意，在一个子程序中中断，去执行其他子程序，不是函数调用，有点类似CPU的中断。比如子程序A、B：
'''

def A():
    print('1')
    print('2')
    print('3')

def B():
    print('x')
    print('y')
    print('z')

def consumer():
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('[CONSUMER] Consumer %s...' % n)
        r = '200 OK'

def produce(c):
    c.send(None)
    n = 0
    while n < 5:
        n = n + 1
        print('[PRODUCE] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCE] Consumer return:%s' % r )
    c.close()

#c = consumer()
#produce(c)
'''
import asyncio

@asyncio.coroutine
def hello():
    print("Hello world")
    # 异步调用 asyncio.sleep(1)
    r = yield from asyncio.sleep(1)
    print("Hello again!")

# 获取EventLoop：
loop = asyncio.get_event_loop()
# 执行coroutine
loop.run_until_complete( hello() )
loop.close()
#loop.run_forever()

'''

import threading
import asyncio

@asyncio.coroutine
def hello():
    print('Hello world! (%s)' % threading.currentThread())
    yield from asyncio.sleep(1)
    print('Hello again! (%s)' % threading.current_thread())

loop = asyncio.get_event_loop()
tasks = [hello(), hello()]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()