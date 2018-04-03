def my_abs(x):
    if not isinstance(x,(int, float)):
        raise TypeError("bad operand type")
    if x >= 0:
        return x
    else:
        return -x

def nop():
    pass

def power(x, n=2):
    s = 1
    while n > 0:
        n = n - 1
        s = s * x
    return s

def f1(a, b, *, c, d):
    print('a =', a, 'b =', b, 'c =', c, 'd =', d)

def f2(a, b, c=0, *, d, **kw):
    print('a =', a, 'b =', b, 'c =', c, 'd =', d, 'kw =', kw)

def add_end(L=[]):
    L.append('END')
    print( L )

def calc(*numbers):
    sum = 0
    for n in numbers:
        sum = sum + n * n
    return sum

def person(name, age, **kw):
    print(name, age, kw)

if __name__ == "__main__":
    extra = {'city': 'Beijing', 'job': 'Engineer'}
    person('Micheal', 30, city="Beijing", job='Engineer')
    person('Tom',40,**extra)
