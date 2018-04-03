#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging; logging.basicConfig(level=logging.INFO)
import os, json, time, sys
from datetime import datetime
import asyncio
from aiohttp import web
import aiomysql
from orm import Model, StringField, create_pool, destroy_pool

if __name__ == "__main__":  # 一个类自带前后都有双下划线的方法，在子类继承该类的时候，这些方法会自动调用，比如__init__
    class User(Model):  # 虽然User类乍看没有参数传入，但实际上，User类继承Model类，Model类又继承dict类，所以User类的实例可以传入关键字参数
        id = StringField('id', primary_key=True)  # 主键为id， tablename为User，即类名
        name = StringField('name')

    # 创建异步事件的句柄
    loop = asyncio.get_event_loop()

    # 创建实例
    @asyncio.coroutine
    def test():
        yield from create_pool(loop=loop, host='localhost', port=3306, user='root', password='123456', db='bk')
        #user = User(id=5, name='Tom')
        user = User()
        #yield from user.save()
        r = yield from user.findAll()
        print('----',r)
        # yield from user.save()
        # yield from user.update()
        # yield from user.delete()
        # r = yield from User2.find(8)
        # print(r)
        # r = yield from User2.findAll()
        # print(1, r)
        # r = yield from User2.findAll(name='sly')
        # print(2, r)
        yield from destroy_pool()  # 关闭pool


    loop.run_until_complete(test())
    loop.close()
    if loop.is_closed():
        sys.exit(0)





