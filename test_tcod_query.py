import requests
import json

url = "http://localhost:8001/query"
payload = {
    "intent": "part_tcod_search",
    "fact": "Y6",
    "as_find": "Z",
    "limit": 50,
    "offset": 0
}
print("=== 요청 payload ===")
print(json.dumps(payload, ensure_ascii=False, indent=2))
print()

try:
    resp = requests.post(url, json=payload, timeout=5)
    print(f"HTTP 상태: {resp.status_code}")
    data = resp.json()
    print(f"intent: {data.get('intent')}")
    print(f"count: {data.get('count')}")
    print(f"message: {data.get('message')}")
    print(f"result 건수: {len(data.get('result', []))}")
    print()
    print("=== query_script ===")
    print(data.get("query_script"))
except Exception as e:
    print(f"오류: {e}")
