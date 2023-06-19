import requests
r = requests.get("http://localhost:4001/custom-greetings", params={"name":"Charles"})
print(r.content)