def application(environ, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    for x, y in environ.items():
        print( x, y )
    print( environ['PATH_INFO'][1:] )
    body = '<h1>Hello, %s!</h1>' % (environ['PATH_INFO'][1:] or 'web')
    return [body.encode('utf-8')]
