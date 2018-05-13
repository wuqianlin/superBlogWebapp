#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'duke.wu'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio
from aiohttp import web
from coroweb import get, post
from apis import Page, APIValueError, APIResourceNotFoundError, APIPermissionError
from models import User, Comment, Blog, next_id
from config import configs
import markdown2
import codecs


COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret

def check_admin(request):
    print(request.__user__, request.__user__.admin)
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError( )

def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user['id'], user['passwd'], expires, _COOKIE_KEY)
    L = [user['id'], expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


@asyncio.coroutine
def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


@get('/')
def index():
    blogs = yield from Blog.findAllOrderBy(created_at='created_at')
    return {
        '__template__': 'operation.html',
        'blogs':blogs
    }

@get('/read')
def get_read():
    blogs = yield from Blog.findblogs_by_tab(tab="read")
    return {
        '__template__': 'operation.html',
        'blogs':blogs
    }

@get('/python')
def get_python():
    blogs = yield from Blog.findblogs_by_tab(tab="python")
    return {
        '__template__': 'operation.html',
        'blogs':blogs
    }

@get('/opera')
def get_opera():
    blogs = yield from Blog.findblogs_by_tab(tab="opera")
    return {
        '__template__': 'operation.html',
        'blogs':blogs
    }

@get('/ai')
def get_ai():
    blogs = yield from Blog.findblogs_by_tab(tab="ai")
    return {
        '__template__': 'operation.html',
        'blogs':blogs
    }

@get('/blog/{id}')
def get_blog(id):
    blog = yield from Blog.find(id)
    print(blog.content)

    #comments = yield from Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    comments = yield from Comment.findAll()
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }


@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }

@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }

@get('/getsignin')
def getsignin():
    return {
        '__template__': 'getsignin.html'
    }

@post('/postinfo')
def getpostinfo(*, email, passwd):
    print("***hello the world")
    print(email)

@post('/api/authenticate')
def authenticate(*, email, passwd):

    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    # users = yield from User.findAll('email=?', [email])
    users = yield from User.findAll( email = email )
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]

    print(email, passwd)
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user['id'].encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    print( 'user[\'passwd\']:', user['passwd']  )
    print( 'sha1.hexdigest():', sha1.hexdigest() )

    if user['passwd'] != sha1.hexdigest():  #####
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user['passwd'] = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/postform')
def postform():
    return {
        '__template__': 'postform.html'
    }

@get('/textarea')
def textarea():
    return {
        '__template__': 'textarea.html'
    }

@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r

@get('/manage/')
def manage():
    return 'redirect:/manage/comments'

@get('/manage/comments')
def manage_comments(*, page='1'):
    return {
        '__template__': 'manage_comments.html',
        'page_index': get_page_index(page)
    }

'''
@get('/manage/blogs')
def manage_blogs(*, page='1'):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }
'''

@get('/manage/blogs/create')
def manage_create_blog():
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'
    }

@get('/manage/blogs/edit')
def manage_edit_blog(*, id):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs/%s' % id
    }

@post('/api/blog_create_save')
def authenticate2(*,user_id,user_name,user_image,name,summary,tab,content_md,private ):
    blog = Blog(user_id=user_id,
                user_name=user_name,
                user_image=user_image,
                name=name,
                summary=summary,
                tab=tab,
                content=content_md,
                private=private)
    yield from blog.save()
    return blog

@post('/api/blogs_delete')
def blogs_delete(*, blog_id):
    blog = yield from Blog.find(pk=blog_id)
    yield from blog.remove()


@get('/api/blogshandle')
def manage_blogs(request):
    check_admin(request)
    blogs = yield from Blog.findAll()
    print(blogs)
    return {
        '__template__': 'blogs_manage.html',
        'blogs':blogs
    }

@post('/api/blogs_edit')
def blogs_edit(*, blog_id):
    blog = yield from Blog.find(pk=blog_id)
    return{
        '__template__': 'edit-for-update.html',
        'id':blog.id,
        'user_id':blog.user_id,
        'user_name':blog.user_name,
        'user_image':blog.user_image,
        'name':blog.name,
        'summary':blog.summary,
        'tab':blog.tab,
        'content':blog.content,
    }

@post('/api/edit_update')
def edit_update(*,id,user_id,user_name,user_image,name,summary,tab,content_md):
    blog = yield from Blog.find(id)
    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content_md.strip()
    blog.tab = tab.strip()
    blog.latestupdated_at = time.time()
    yield from blog.update()

@get('/manage/users')
def manage_users(*, page='1'):
    return {
        '__template__': 'manage_users.html',
        'page_index': get_page_index(page)
    }

@get('/api/comments')
def api_comments(*, page='1'):
    page_index = get_page_index(page)
    num = yield from Comment.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = yield from Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)

@post('/md')
def editor_md( submit ):
    print( submit )

@post('/api/blogs/{id}/comments')
def api_create_comment(id, request, *, content):
    user = request.__user__
    if user is None:
        raise APIPermissionError('Please signin first.')
    if not content or not content.strip():
        raise APIValueError('content')
    blog = yield from Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
    yield from comment.save()
    return comment

@post('/api/comments/{id}/delete')
def api_delete_comments(id, request):
    check_admin(request)
    c = yield from Comment.find(id)
    if c is None:
        raise APIResourceNotFoundError('Comment')
    yield from c.remove()
    return dict(id=id)

@get('/api/users')
def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    num = yield from User.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = yield from User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


@post('/api/users')
def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    #users = yield from User.findAll('email=?', [email])
    users = yield from User.findAll( email= email)
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    print( sha1_passwd )
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    #print()
    yield from user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

@get('/api/blogs')
def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = yield from Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = yield from Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)

@get('/api/blogs/{id}')
def api_get_blog(*, id):
    blog = yield from Blog.find(id)
    return blog


@post('/api/blogs')
def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name=name.strip(), summary=summary.strip(), content=content.strip())
    yield from blog.save()
    return blog


@post('/api/blogs/{id}')
def api_update_blog(id, request, *, name, summary, content):
    check_admin(request)
    blog = yield from Blog.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    yield from blog.update()
    return blog


@post('/api/blogs/{id}/delete')
def api_delete_blog(request, *, id):
    check_admin(request)
    blog = yield from Blog.find(id)
    yield from blog.remove()
    return dict(id=id)
