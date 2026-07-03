import requests

try:
    url = "http://localhost:8001/query"
    payload = {
        "intent": "vend_search",
        "fact": "K1",
        "as_find": "LG"
    }
    print("Sending POST request to FastAPI server...")
    resp = requests.post(url, json=payload)
    print("Status code:", resp.status_code)
    data = resp.json()
    print("Intent:", data.get("intent"))
    print("Count:", data.get("count"))
    print("Message:", data.get("message"))
    results = data.get("result", [])
    print("First 5 results:")
    for r in results[:5]:
        print(r)
except Exception as e:
    print("Error:", e)
