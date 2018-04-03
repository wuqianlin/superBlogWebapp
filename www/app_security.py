#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Models for user, blog, comment.
'''

__author__ = 'QianlinWu'

import time, uuid
from functools import reduce
from operator import or_

from orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField
from flask_security import RoleMixin

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)
    roles = Role

    def can(self, permissions):
        if self.roles is None:
            return False
        all_perms = reduce(or_, map(lambda x: x.permissions, self.roles))
        return all_perms & permissions == permissions

    def can_admin(self):
        return self.can(Permission.ADMINISTER)


class Permission(object):
    LOGIN = 0x01
    EDITOR = 0x02
    OPERATOR = 0x04
    ADMINISTER = 0xff
    PERMISSION_MAP = {
        LOGIN:('login','Login user'),
        EDITOR:('editor','Editor'),
        OPERATOR:('op','Operator'),
        ADMINISTER:('admin','Super administrator')
    }

class Role(Model):
    __table__ = 'role'

    id = IntegerField(primary_key=True )
    name = StringField(ddl='varchar(50)')
    permissions = IntegerField(primary_key=True, default=Permission.LOGIN )
    description = StringField(ddl='varchar(100)')


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def _deco(*args, **kwargs):
            if not current_user.can(permissioin):
                abort(403)
        




