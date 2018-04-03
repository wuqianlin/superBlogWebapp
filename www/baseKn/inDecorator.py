'''
def log(func):
    def wrapper(*args, **kw):
        print('call %s():' % func.__name__)
        return func(*args, **kw)
    return wrapper

@log
def now():
    print('2015-3-25')

now()
'''


'''
def log(text):
    def decorator(func):
        def wrapper(*args, **kw):
            print('%s %s()' % (text, func.__name__))
            return func(*args, **kw)
        return wrapper
    return decorator

@log('execute')
def now():
    print('2015-3-25')

now()
print(now.__name__)
'''

'''
# 不带参数的decorator
import functools

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        print('%s %s()' % (text, func.__name__))
        return func(*args, **kw)
    return wrapper
'''

# 带参数的 decorator
import functools

def log(text):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kw):
            print('%s %s():' % ( text, func.__name__ ))
            return func(*args, **kw)
        return wrapper
    return decorator

@log('execute')
def now():
    print('2015-3-25')

now()
print(now.__name__)


