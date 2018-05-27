# -*- coding: utf-8 -*-

__author__ = 'duke.wu'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio
from aiohttp import web
from coroweb import get, post
from apis import Page, APIValueError, APIResourceNotFoundError, APIPermissionError
from models import User, Comment, Blog, Label, next_id
from config import configs
import markdown2
import markdown
import codecs
import mistune


COOKIE_NAME = 'awesession'
COOKIE_BLOG = 'blogid'
_COOKIE_KEY = configs.session.secret


def check_admin(request):
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
        '__template__': 'itemlist.html',
        'blogs':blogs
    }


@get('/project/{name}')
def project_list(name):
    blogs = yield from Blog.findAll(label=name)
    return {
        '__template__': 'itemlist.html',
        'blogs':blogs
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


@post('/api/authenticate')
def authenticate(*, email, passwd):

    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    #users = yield from User.findAll('email=?', [email])
    users = yield from User.findAll(email = email)
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]

    # check password:
    sha1 = hashlib.sha1()
    sha1.update(user['id'].encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    print( 'user[\'passwd\']:', user['passwd']  )
    print( 'sha1.hexdigest():', sha1.hexdigest() )

    if user['passwd'] != sha1.hexdigest():
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

@get('/manage/blogs')
def manage_blogs(request):
    check_admin(request)
    blogs = yield from Blog.findAll()
    print(blogs)
    return {
        '__template__': 'blogs_manage.html',
        'blogs':blogs
    }

'''
@get('/manage/blogs')
def manage_blogs(*, page='1'):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }
'''


@get('/manage/editor')
def create_editor_page():
    return {
        '__template__': 'editor.html',
    }


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
def api_blogs(request,*, page='1'):
    check_admin(request)
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
    #comments = yield from Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    comments = yield from Comment.findAll()
    for c in comments:
        c['html_content'] = text2html(c['content'])

    #input_file = codecs.open('test.md', mode="r", encoding="utf-8")
    #text = input_file.read()
    #html = markdown.markdown(text)
    #blog.html_content = markdown.markdown( blog.content )
    #blog.html_content = markdown.markdown(text, safe_mode="escape")

    markdown = mistune.Markdown()
    blog.html_content = markdown(blog.content)

    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }


@post('/api/blogs')
def api_create_blog(request, *, name, content, label, limit, blogid=''):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    #if not content or not content.strip():
    #    raise APIValueError('content', 'content cannot be empty.')
    if blogid == '':
        blog = Blog(user_id = request.__user__.id,
                    user_name = request.__user__.name,
                    user_image = request.__user__.image,
                    name = name,
                    label = label,
                    content = content,
                    limit = limit)
        yield from blog.save()
        return json.dumps(blog.id)
    else:
        blog = yield from Blog.find(pk=blogid)
        blog.id = blogid,
        blog.user_id = request.__user__.id,
        blog.user_name = request.__user__.name,
        blog.user_image = request.__user__.image,
        blog.name = name,
        blog.label = label,
        blog.content = content,
        blog.limit = limit
        yield from blog.update( )
        return json.dumps(blog.id)


@get('/api/blogs/{id}/edit')
def blogs_edit(id,request):
    check_admin(request)
    blog = yield from Blog.find(pk=id)
    return{
        '__template__': 'modify.html',
        'blog': blog
    }


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
def api_delete_blog(id, request):
    check_admin(request)
    blog = yield from Blog.find(pk=id)
    yield from blog.remove()
    logging.info("博客删除成功！！！")
    data = dict()
    data.setdefault("msc","删除成功")
    data.setdefault("code","2000")
    data.setdefault("blog_id", id)
    return json.dumps(data)


@get('/api/lables')
def api_get_lables( ):
    blog = yield from Label.findAll( )
    return json.dumps( blog )