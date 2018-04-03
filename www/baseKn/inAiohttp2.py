import asyncio
import aiohttp
import urllib.request as request
from bs4 import BeautifulSoup as bs

async def hello():
    async with aiohttp.get('https://www.baidu.com/') as r:
        # text()可以在括号中指定解码方式，编码方式
        print( await r.text(encoding='windows-1251') )
    async with aiohttp.get('http://www.guxiansheng.cn/img/download_bg.png') as jpg:
        # 或者也可以选择编码，适合读取图像
        print( await jpg.read() )

async def timeoutHello():
    # 注意，设置的时间类型和大小
    with aiohttp.Timeout(1):
        async with aiohttp.get('https://www.baidu.com/') as r:
            print( await r.text() )

async def sessionHello():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.baidu.com/') as resp:
            print( resp.status )
            print( await resp.text() )

    '''如果要使用post方法，则相应的语句要改成
        session.post('http://httpbin.org/post', data=b'data')'''

async def headersHello():
    url = 'https://www.baidu.com/'
    headers = {'content-type':'application/json'}
    async with aiohttp.ClientSession() as session:
        await session.get(url, headers=headers)

async def cookieHello():
    url = 'https://www.baidu.com/'
    tt = {'cookies_are':'working'}
    async with aiohttp.ClientSession( tt ) as session:
        async with session.get(url) as resp:
            assert await resp.json() == {"cookies":{"cookies_are":"working"}}

'''
tasks=['hello()','timeoutHello()']
loop = asyncio.get_event_loop()
loop.run_until_complete( cookieHello() )
loop.close()
'''
def encode(s):
    return ' '.join([bin(ord(c)).replace('0b', '') for c in s])

def decode(s):
    return ''.join([chr(i) for i in [int(b, 2) for b in s.split(' ')]])

def saveHtml(html_list):
    with open('D:\Desktop\html.txt','w') as fd:
        fd.write( html_list )

async def getPage(url,res_list):
    #print(url)
    headers = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            assert resp.status == 200
            res_list.append( await resp.text() )
            tt = encode( str(res_list) )
            #print( tt )

            saveHtml(tt)
            #print(res_list)

class parseListPage():
    def __init__(self, page_str):
        self.page_str = page_str
    def __enter__(self):
        page_str = self.page_str
        page = bs(page_str,'lxml')
        articles = page.find_all( 'div', attrs={'class':'article_title'} )
        art_urls = []
        for a in articles:
            x = a.find('a')['href']
            art_urls.append('http://blog.csdn.net' + x)
        #print( art_urls )
        return art_urls

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

'''
loop = asyncio.get_event_loop()
tasks = [hello(), timeoutHello()]
loop.run_until_complete(asyncio.wait( tasks ))
loop.close()
'''


page_num = 5
page_url_base = 'http://blog.csdn.net/u014595019/article/list/'
page_urls = [page_url_base + str(i+1) for i in range(page_num)]
#print([x for x in page_urls])

loop = asyncio.get_event_loop()
ret_list = []
tasks = [getPage(host,ret_list) for host in page_urls]
loop.run_until_complete( asyncio.wait(tasks) )

articles_url = []
for ret in ret_list:
    with parseListPage(ret) as tmp:
        articles_url += tmp
ret_list = []

tasks = [getPage(url, ret_list) for url in articles_url]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
