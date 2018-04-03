import json
import requests

url = 'http://www.wuqianlin.cn/static/editor.md/examples/simple.html'
payload = {'some':'data'}
headers = {'content-type':'application/json'}

r = requests.post(url, data=json.dumps(payload),headers=headers)

print(r.text)