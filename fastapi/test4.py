import requests
payload = {
  "title": "This is my great blog title",
  "content": "This is the body of my article",
  "Author": "Jaskier",
  "avg_reading_time": 5,
  "category": "Tech", 
  "tags": ["Name_1"] 
}
r = requests.post("http://localhost:4001/create-blog-article", json=payload)
print(r.content)