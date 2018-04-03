# _*_ coding: utf-8 _*_

# 导入:
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()

# 定义User对象:
class User(Base):
    # 表的名字:
    __tablename__ = 'user'

    # 表的结构:
    id = Column(String(20), primary_key=True)
    name = Column(String(20))
'''
class User(Base):
    __tablename__ = 'user'

    id = Column(String(20), primary_key=True)
    name = Column(String(20))
    # 一对多:
    books = relationship('Book')

class Book(Base):
    __tablename__ = 'book'

    id = Column(String(20), primary_key=True)
    name = Column(String(20))
    # “多”的一方的book表是通过外键关联到user表的:
    user_id = Column(String(20), ForeignKey('user.id'))
'''


# 初始化数据库连接:
'''
create_engine()用来初始化数据库连接。SQLAlchemy用一个字符串表示连接信息：
    '数据库类型+数据库驱动名称://用户名:口令@机器地址:端口号/数据库名'
'''
engine = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/bk')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

'''
session = DBSession()  # 创建session对象:
new_user = User(id='6', name='Jim')  # 创建新User对象:
session.add(new_user)  # 添加到session:
session.commit()  # 提交即保存到数据库:
session.close()  # 关闭session:
'''

# 创建Session:
session = DBSession()
# 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
user = session.query(User).filter(User.id=='6').one()
# 打印类型和对象的name属性:
print('type:', type(user))
print('name:', user.name)
# 关闭Session:
session.close()







