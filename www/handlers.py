# -*- coding: utf-8 -*-

__author__ = 'duke.wu'

' url handlers '
import mistune
import re
import time
import json
import hashlib
import asyncio
from aiohttp import web
from coroweb import get, post
from apis import Page, APIValueError, APIResourceNotFoundError, APIPermissionError, APIError
from models import User, Comment, Blog, Label, next_id
from config import configs
from utils import logger


COOKIE_NAME = 'awesession'
COOKIE_BLOG = 'blogid'
_COOKIE_KEY = configs.session.secret


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError("没有授权")


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
    """
    Generate cookie str by user.
    """
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
    """
    Parse cookie and load user if cookie is valid.
    """
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from User.get(id=uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logger.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logger.exception(e)
        return None


@get('/waterfall')
def waterfall():
    return {
        '__template__': 'waterfall.html',
    }


@get('/')
def index():
    return {
        '__template__': 'blogslist.html',
    }


@get('/api/brief')
def get_blogs_brief(request):
    page = request.query.get('page', 1)
    page = int(page)
    size = request.query.get('size', 10)
    size = int(size)
    info = str()

    if size <= 0 or size > 15:
        size = 10
        info = 'warning: 每页数量范围为(1 ~ 15)!'
    if page <= 0:
        page = 1
        info = 'warning: 你的页码数不正确，应该正整数！'
    blog_count = yield from Blog.count()
    max_page = blog_count / size
    if max_page > int(max_page):
        max_page = int(max_page) + 1
    if page > max_page:
        info = 'warning: 页码数应小于等于最大页码数！'

    start_step = (page - 1) * size
    sql = "select `id`,`user_id`,`user_name`,`user_image`,`name`,`summary`," \
          "SUBSTRING(content,1,150) AS `content`,`limit`,`label`,`read_total`," \
          "`created_at`,`latestupdated_at` from blogs ORDER BY `created_at` DESC limit %i, %i;" % (start_step, size)
    blogs = yield from Blog.execute(sql)
    if blogs:
        status = 'success'
        if len(blogs) < size:
            info = "warning: 这是最后一页了！"
        for blog in blogs:
            comments = yield from Comment.filter(blog_id=blog.get("id"))
            comments_amount = len(comments)
            blog.setdefault('comments_amount', comments_amount)
    else:
        status = 'failed'
    content = dict(status=status,
                   page=page,
                   size=size,
                   max_page=max_page,
                   info=info,
                   data=blogs,)
    return content


@get('/project/{name}')
def project_list(name):
    blogs = yield from Blog.filter(label=name)
    return {
        '__template__': 'blogslist.html',
        'blogs': blogs
    }


@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }


@get('/signin')
def signin(request):
    logger.info(dir(request))
    return {
        '__template__': 'signin.html'
    }


@get('/getsignin')
def getsignin():
    return {
        '__template__': 'getsignin.html'
    }


@get('/api/doc_info')
def getsignin():
    doc_info = dict()
    rs_blog = yield from Blog.count()
    rs_comment = yield from Comment.count()
    doc_info.setdefault('rs_blog', rs_blog[0])
    doc_info.setdefault('rs_comment', rs_comment[0])
    return json.dumps(doc_info)


@post('/api/authenticate')
def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = yield from User.filter(email=email)
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]

    # check password:
    sha1 = hashlib.sha1()
    sha1.update(user['id'].encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    logger.info('user[\'passwd\']:', user['passwd'])
    logger.info('sha1.hexdigest():', sha1.hexdigest())

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
    logger.info('user signed out.')
    return r


@get('/manage/')
def manage():
    return 'redirect:/manage/blogs'


@get('/manage/comments')
def manage_comments(*, page='1'):
    return {
        '__template__': 'manage_comments.html',
        'page_index': get_page_index(page)
    }


@get('/manage/blogs')
def manage_blogs(request):
    check_admin(request)
    blogs = yield from Blog.all(order_by='created_at desc')
    return {
        '__template__': 'blogs_manage.html',
        'blogs': blogs
    }


"""
@get('/manage/blogs')
def manage_blogs(*, page='1'):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }
"""


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
    num = yield from Comment.count()
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = yield from Comment.filter(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)


@post('/md')
def editor_md(submit):
    logger.info(submit)


@post('/api/blogs/{id}/comments')
def api_create_comment(id, request, *, content, parent_id=''):

    user = request.__user__
    if user is None:
        # raise APIPermissionError('Please signin first.')
        return json.dumps('success')

    if not content or not content.strip():
        raise APIValueError('content')
    blog = yield from Blog.get(id=id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')

    at_who = ''
    if content.startswith('@'):
        content_tmp = content.strip('@').split(' ', 1)
        at_who = content_tmp[0]
        if content_tmp[1]:
            content = content_tmp[1]
        else:
            content = ''

    comment = Comment(blog_id=blog.id,
                      user_id=user.id,
                      user_name=user.name,
                      parent_id=parent_id,
                      at_who=at_who,
                      user_image=user.image,
                      content=content.strip())
    yield from comment.save()
    return comment


@get('/api/blogs/{id}/comments_amount')
def api_get_comment_amount(id, request):
    """根据 blog id 获取评论数"""
    comments = yield from Comment.filter(blog_id=id)
    comments_amount = len(comments)
    return json.dumps(comments_amount)


@get('/api/blogs/{id}/comments')
def api_get_comment(id, request):
    user = request.__user__
    if user is None:
        raise APIPermissionError('Please signin first.')
    comments = yield from Comment.filter(blog_id=id)
    if comments is None:
        raise APIResourceNotFoundError('Comment')

    parent_comments = list()
    child_comments = list()
    for item in comments:
        if item['parent_id'] == '':
            parent_comments.append(item)
        else:
            child_comments.append(item)
    for x in parent_comments:
        child_comments_list = list()
        for y in child_comments:
            if x.get('id') == y.get('parent_id'):
                child_comments_list.append(y)
        x.setdefault('child_comments', child_comments_list)
    return json.dumps(parent_comments)


@post('/api/comments/{id}/delete')
def api_delete_comments(id, request):
    check_admin(request)
    c = yield from Comment.get(id=id)
    if c is None:
        raise APIResourceNotFoundError('Comment')
    yield from c.remove()
    return dict(id=id)


@get('/api/users')
def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    num = yield from User.count()
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = yield from User.filter(orderBy='created_at desc', limit=(p.offset, p.limit))
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
    users = yield from User.filter( email= email)
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    logger.info(sha1_passwd)
    user = User(id=uid,
                name=name.strip(),
                email=email,
                passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    yield from user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@post('/api/visitors')
def api_register_visitor(*, name, email, site, private=0):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')

    users = yield from User.filter(email=email)
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')

    uid = next_id()
    user = User(id=uid,
                name=name.strip(),
                email=email,
                site=site,
                private=private
                )
    yield from user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/api/blogs')
def api_blogs(request, *, page='1'):
    check_admin(request)
    page_index = get_page_index(page)
    num = yield from Blog.count()
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blog = yield from Blog.filter(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blog)


def get_comments(blog_id):

    comments = yield from Comment.filter(blog_id=blog_id)
    if comments is None:
        raise APIResourceNotFoundError('Comment')

    parent_comments = list()
    child_comments = list()
    for item in comments:
        if item['parent_id'] == '':
            parent_comments.append(item)
        else:
            child_comments.append(item)
    for x in parent_comments:
        child_comments_list = list()
        for y in child_comments:
            if x.get('id') == y.get('parent_id'):
                child_comments_list.append(y)
        x.setdefault('child_comments', child_comments_list)

    return parent_comments


@get('/api/blogs/{id}')
def api_get_blog(*, id):
    blog = yield from Blog.get(id=id)
    if blog:
        blog.read_total += 1
        yield from blog.update()

    # comments = get_comments(id)
    comments = yield from Comment.filter(blog_id=id)
    if comments is None:
        raise APIResourceNotFoundError('Comment')

    parent_comments = list()
    child_comments = list()
    for item in comments:
        for c in comments:
            c['html_content'] = text2html(c['content'])
        if item['parent_id'] == '':
            parent_comments.append(item)
        else:
            child_comments.append(item)
    for x in parent_comments:
        child_comments_list = list()
        for y in child_comments:
            if x.get('id') == y.get('parent_id'):
                child_comments_list.append(y)
        x.setdefault('child_comments', child_comments_list)

    #input_file = codecs.open('test.md', mode="r", encoding="utf-8")
    #text = input_file.read()
    #html = markdown.markdown(text)
    #blog.html_content = markdown.markdown( blog.content )
    #blog.html_content = markdown.markdown(text, safe_mode="escape")

    markdown = mistune.Markdown()
    blog.html_content = markdown(blog.content)

    return {
        '__template__': 'blogs.html',
        'blog': blog,
        'comments': parent_comments
    }


@post('/api/blogs')
def api_create_blog(request, *, name, content, label, limit, blogid=''):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    # if not content or not content.strip():
    #    raise APIValueError('content', 'content cannot be empty.')
    if blogid == '':
        blog = Blog(user_id=request.__user__.id,
                    user_name=request.__user__.name,
                    user_image=request.__user__.image,
                    name=name,
                    label=label,
                    content=content,
                    limit=limit)
        yield from blog.save()
        return json.dumps(blog.id)
    else:
        blog = yield from Blog.get(id=blogid)
        blog.id = blogid,
        blog.user_id = request.__user__.id,
        blog.user_name = request.__user__.name,
        blog.user_image = request.__user__.image,
        blog.name = name,
        blog.label = label,
        blog.content = content,
        blog.limit = limit
        yield from blog.update()
        return json.dumps(blog.id)


@get('/api/blogs/{id}/edit')
def blogs_edit(id, request):
    check_admin(request)
    blog = yield from Blog.get(id=id)
    return{
        '__template__': 'modify.html',
        'blog': blog
    }


@post('/api/blogs/{id}')
def api_update_blog(id, request, *, name, summary, content):
    check_admin(request)
    blog = yield from Blog.get(id=id)
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
    blog = yield from Blog.get(id=id)
    yield from blog.remove()
    logger.info("博客删除成功！！！")
    data = dict()
    data.setdefault("msc","删除成功")
    data.setdefault("code","2000")
    data.setdefault("blog_id", id)
    return json.dumps(data)


@get('/api/lables')
def api_get_lables( ):
    blog = yield from Label.all()
    return json.dumps(blog)


@get('/api/blogs-summary')
def api_get_blogs_summary():
    sql = "select `id`,`user_id`,`user_name`,`user_image`,`name`,`summary`," \
          "SUBSTRING(content,1,150) AS `content`,`limit`,`label`,`read_total`," \
          "`created_at`,`latestupdated_at` from blogs ORDER BY `created_at` DESC;"

    blogs = yield from Blog.execute2(sql)

    if blogs:
        for blog in blogs:
            comments = yield from Comment.filter(blog_id=blog.get("id"))
            comments_amount = len(comments)
            blog.setdefault('comments_amount', comments_amount)
    return {
        '__template__': 'blogslist.html',
        'blogs': blogs
    }
