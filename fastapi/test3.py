import requests

r = requests.get("http://localhost:4001/blog-articles/0")
print(r.content)