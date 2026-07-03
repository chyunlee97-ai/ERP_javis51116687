import requests
import json

base = "http://localhost:8002"

# 1. 헬스체크
try:
    r = requests.get(f"{base}/health", timeout=3)
    print(f"Health: {r.json()}")
except Exception as e:
    print(f"헬스체크 실패: {e}")
    
# 2. part_tcod_search 테스트 (Y6, Z)
payload = {
    "intent": "part_tcod_search",
    "fact": "Y6",
    "as_find": "Z",
    "limit": 50,
    "offset": 0
}
print(f"\n요청: {json.dumps(payload, ensure_ascii=False)}")
try:
    r = requests.post(f"{base}/query", json=payload, timeout=10)
    data = r.json()
    print(f"HTTP: {r.status_code}")
    print(f"intent: {data.get('intent')}")
    print(f"count: {data.get('count')}")
    print(f"message: {data.get('message')}")
    qs = data.get("query_script")
    print(f"query_script: {'있음 (' + str(len(qs)) + '자)' if qs else 'None'}")
    if qs:
        print("=== SQL ===")
        print(qs)
except Exception as e:
    print(f"실패: {e}")
