'''
import requests
def hello():
    return requests.get("http://httpbin.org/get")

print(hello().text)
'''

import asyncio
from aiohttp import ClientSession

'''
async def hello():
    # 首先异步获取相应
    async with ClientSession() as session:
        # 异步读取相应内容
        async with session.get("http://httpbin.org/get") as response:
            response = await response.read()
            print(response)
'''

async def fetch(url):
    async with ClientSession() as sessioin:
        async with sessioin.get(url) as response:
            return response.read()

async def run(loop, r):
    url = "http://httpbin.org/get"
    tasks=[]
    for i in range(r):
        task = asyncio.ensure_future(fetch(url))
        tasks.append(task)
        #注意asyncio.gather()的用法，它搜集所有的Future对象，然后等待他们返回。
        responses = await asyncio.gather(*tasks)
        print(responses)

def print_responses(result):
    print(result)

loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(loop, 4))
loop.run_until_complete(future)

'''
loop = asyncio.get_event_loop()
tasks = []
url = "http://httpbin.org/get"
for i in range(5):
    task = asyncio.ensure_future(hello( ))
    tasks.append(task)
loop.run_until_complete(asyncio.wait(tasks))
'''
