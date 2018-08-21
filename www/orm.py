#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import uuid
import logging
import asyncio
import aiomysql

logging.basicConfig(level=logging.INFO)


# 记录SQL语句执行日志
def log(sql):
    logging.info('SQL:  %s' % sql)


"""
    aiomysql为MySQL数据库提供了异步IO的驱动。
    由于Web框架使用了基于asyncio的aiohttp，这是基于协程的异步模型。
"""


@asyncio.coroutine
def create_pool(_loop, **kw):
    """
    创建一个全局的连接池，每个HTTP请求都可以从连接池中直接获取数据库连接。
    使用连接池的好处是不必频繁地打开和关闭数据库连接，而是能复用就尽量复用。
    连接池由全局变量__pool存储，缺省情况下将编码设置为utf8，自动提交事务：
    要执行SELECT语句，我们用select函数执行，需要传入SQL语句和SQL参数：
    """
    logging.info('create database connection pool...')
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
        loop=_loop
    )


@asyncio.coroutine
def destroy_pool():
    global __pool
    if __pool is not None:
        __pool.close()
        yield from __pool.wait_closed()


@asyncio.coroutine
def select(sql, args=(), size=None):
    log(sql)
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
        return rs


@asyncio.coroutine
def execute(sql, args=()):
    """
    要执行INSERT、UPDATE、DELETE语句，
    可以定义一个通用的execute()函数，
    因为这3种SQL的执行都需要相同的参数，
    以及返回一个整数表示影响的行数：
    execute()函数和select()函数所不同的是，cursor对象不返回结果集，而是通过rowcount返回结果数。
    """
    log(sql)
    with (yield from __pool) as conn:
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount
            yield from cur.close()
        except BaseException as e:
            raise e
        return affected


def create_args_string(num):
    l = []
    for n in range(num):
        l.append('?')
    return ', '.join(l)


class Field(object):
    """表的字段包含名字，类型，是否为表的主键和默认值
    返回 表名字 字段名 和字段类型
    """
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)


################################################################################
# 定义数据库中五个存储类型
################################################################################

class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)


class BooleanField(Field):
    """布尔类型不可以作为主键"""
    def __init__(self, name=None, default=False):
        super().__init__(name, 'Boolean', False, default)


class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'int', primary_key, default)


class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'float', primary_key, default)


class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


class MetaModel(type):
    """MetaModel 主要是为一个数据库表映射成一个封装的类做准备:
    读取具体子类的映射信息
    创造类的时候，排除对Model类的修改
    在当前类中查找所有的类属性(attrs)，如果找到Field属性，就将其保存到__mappings__的dict中，
    同时从类属性中删除Field (防止实例属性遮住类的同名属性)
    将数据库表名保存到__table__中
    完成这些工作就可以在Model中定义各种数据库的操作方法
    metaclass是类的模板，所以必须从type 类派生
    """

    def __new__(mcs, name, bases, attrs):
        # 排除Model类本身
        if name == 'Model':
            return type.__new__(mcs, name, bases, attrs)

        # 获取table名称
        table_name = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, table_name))

        # 获取所有的Field和主键名
        mappings = dict()
        fields = []
        primary_key = None
        for key, value in attrs.items():
            if isinstance(value, Field):
                logging.info('  found mapping: %s ==> %s' % (key, value))
                mappings[key] = value
                if value.primary_key:
                    # 找到主键:
                    if primary_key:
                        raise RuntimeError('Duplicate primary key for field: %s' % key)
                    primary_key = key
                else:
                    fields.append(key)
        if not primary_key:
            raise RuntimeError('Primary key not found.')

        # 从类属性中删除Field 属性
        for k in mappings.keys():
            attrs.pop(k)

        # 将除主键外的其他属性变成`id`, `name`这种形式
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        # 保存属性和列的映射关系
        attrs['__mappings__'] = mappings
        # 保存表名
        attrs['__table__'] = table_name
        # 主键属性名
        attrs['__primary_key__'] = primary_key
        # 除主键外的属性名
        attrs['__fields__'] = fields

        # 构造默认的SELECT, INSERT, UPDATE和DELETE语句:
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primary_key, ', '.join(escaped_fields), table_name)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (table_name, ', '.join(escaped_fields), primary_key, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (table_name, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primary_key)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (table_name, primary_key)
        attrs['__count__'] = 'select count(*) as `record_amount` from `%s`' % table_name
        return type.__new__(mcs, name, bases, attrs)


################################################################################
# 定义所有ORM映射的基类Model
################################################################################

class Model(dict, metaclass=MetaModel):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def get_value(self, key):
        return getattr(self, key, None)

    def get_value_or_default(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value

    @classmethod
    @asyncio.coroutine
    def all(cls, **kw):
        sql = [cls.__select__]
        args = []

        order_by = kw.get('order_by', None)
        if order_by:
            sql.append('order by')
            sql.append(order_by)

        limit = kw.get('limit', None)
        if limit:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?,?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value : %s ' % str(limit))

        rs = yield from select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    @asyncio.coroutine
    def filter(cls, **kw):
        if len(kw) == 0:
            rs = yield from select(cls.__select__, None)
        else:
            args = []
            values = []
            for k, v in kw.items():
                args.append('%s=?' % k)
                values.append(v)
            rs = yield from select('%s where %s ' % (cls.__select__, ' and '.join(args)), values)
        return [cls(**r) for r in rs]

    @classmethod
    @asyncio.coroutine
    def get(cls, **kw):
        if len(kw) == 0:
            rs = yield from select(cls.__select__, None)
        else:
            args = []
            values = []
            for k, v in kw.items():
                args.append('%s=?' % k)
                values.append(v)
            rs = yield from select('%s where %s ' % (cls.__select__, ' and '.join(args)), values)
        if len(rs) == 0:
            return None
        else:
            return cls(**rs[0])

    @classmethod
    @asyncio.coroutine
    def count(cls):
        sql = 'select count(*) as __num__ from `%s`' % cls.__table__
        args = []
        rs = yield from select(sql, args)
        if len(rs) == 0:
            return None
        return rs[0]['__num__']

    @classmethod
    @asyncio.coroutine
    def execute(cls, sql):
        rs = select(sql)
        return rs

    @asyncio.coroutine
    def save(self):
        args = list(map(self.get_value_or_default, self.__fields__))
        args.append(self.get_value_or_default(self.__primary_key__))
        rows = yield from execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)

    @asyncio.coroutine
    def update(self):
        args = list(map(self.get_value, self.__fields__))
        args.append(self.get_value(self.__primary_key__))
        rows = yield from execute(self.__update__, args)
        if rows != 1:
            logging.warning('failed to update record: affected rows: %s' % rows)

    @asyncio.coroutine
    def delete(self):
        args = [self.get_value(self.__primary_key__)]
        rows = yield from execute(self.__delete__, args)
        if rows != 1:
            logging.warning('failed to delete by primary key: affected rows: %s' % rows)

    @asyncio.coroutine
    def remove(self):
        args = [self.get_value(self.__primary_key__)]
        rows = yield from execute(self.__delete__, args)
        if rows != 1:
            logging.warning('failed to remove by primary key: affected rows: %s' % rows)


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class Label(Model):
    __table__ = 'labels'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(8)')
    label = StringField(ddl='varchar(50)')
    explain = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)


class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    label = StringField(ddl='varchar(50)')
    read_total =  IntegerField(default=0)
    limit = BooleanField()
    created_at = FloatField(default=time.time)
    latestupdated_at = FloatField(default=time.time)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def test_example():
        kw = {'user': 'dukeBlogWeb',
              'db': 'awesome',
              'host': '118.24.1.107',
              'port': 3306,
              'password': 'dukeBlogWeb12*&sd3!@#'}
        yield from create_pool(loop, **kw)

        sql = "select `id`,`user_id`,`user_name`,`user_image`,`name`,`summary`," \
              "SUBSTRING(content,1,150) AS `content`,`limit`,`label`,`read_total`," \
              "`created_at`,`latestupdated_at` from blogs ORDER BY `created_at` DESC limit %i, %i;"

        blogs = yield from Blog.execute(sql % (2, 12))

        if blogs:
            for blog in blogs:
                print(blog)

        a = yield from Blog.count()
        print(a)

        __pool.close()
        yield from __pool.wait_closed()

    loop.run_until_complete(test_example())

