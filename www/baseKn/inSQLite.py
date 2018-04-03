# _*_ coding: utf-8 _*_

'''
在Python中操作数据库时，要先导入数据库对应的驱动，然后，通过Connection对象和Cursor对象操作数据。
要确保打开的Connection对象和Cursor对象都正确地被关闭，否则，资源就会泄露。
如何才能确保出错的情况下也关闭掉Connection对象和Cursor对象呢？请回忆try:...except:...finally:...的用法。

使用Python的DB-API时，只要搞清楚Connection和Cursor对象，打开后一定记得关闭，就可以放心地使用。
使用Cursor对象执行insert，update，delete语句时，执行结果由rowcount返回影响的行数，就可以拿到执行结果。
使用Cursor对象执行select语句时，通过featchall()可以拿到结果集。结果集是一个list，每个元素都是一个tuple，对应一行记录。
如果SQL语句带有参数，那么需要把参数按照位置传递给execute()方法，有几个?占位符就必须对应几个参数，例如：
cursor.execute('select * from user where name=? and pwd=?', ('abc', 'password'))
'''

# 导入SQLite驱动:
import sqlite3

# 连接到SQLite数据库
# 数据库文件是test.db
# 如果文件不存在，会自动在当前目录创建:
conn = sqlite3.connect('test.db')
cursor = conn.cursor()  # 创建一个Cursor:
# 执行一条SQL语句，创建user表:
cursor.execute('create table user1 (id varchar(20) primary key, name varchar(20))')
# 继续执行一条SQL语句，插入一条记录:
cursor.execute('insert into user1 (id, name) values (\'1\', \'Michael\')')
cursor.rowcount  # 通过rowcount获得插入的行数:
cursor.close()  # 关闭Cursor:
conn.commit()  # 提交事务:
conn.close()  # 关闭Connection:


conn = sqlite3.connect('test.db')
cursor = conn.cursor()  # 执行查询语句:
cursor.execute('select * from user where id=?', ('1',))  # 获得查询结果集:
values = cursor.fetchall()
print(values)
cursor.close()
conn.close()
