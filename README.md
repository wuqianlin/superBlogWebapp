# awesome-python-webapp

站点技术规划：
	[root@duke ~]# python3.5 --version
    Python 3.5.2
	
异步框架aiohttp
    $ pip3 install aiohttp
	
前端模板引擎jinja2：
    $ pip3 install jinja2
	
MySQL的Python异步驱动程序aiomysql：
    $ pip3 install aiomysql
    

http://127.0.0.1:9000/blogs_edit
http://127.0.0.1:9000/static/editor_md/examples/simple.html

edit-for-update.html

#### 新建blog
    
	GET:    http://127.0.0.1:9000/static/editor_md/examples/form-get-value2.html
	POST:   http://127.0.0.1:9000/blog_create_save
	
#### blog删除
    
	GET:    http://127.0.0.1:9000/blogshandle
        POST:   http://127.0.0.1:9000/blogs_delete

#### 编辑blog

	GET:    http://127.0.0.1:9000/blogs_edit
	POST:   http://127.0.0.1:9000/edit_update

#### blog后台管理

	GET:    http://127.0.0.1:9000/blogshandle
        POST:   http://127.0.0.1:9000/edit_update


<class 'aiohttp.web_request.Request'>	

#### 首页栏目链接

    CET:    http://127.0.0.1:9000/read
	