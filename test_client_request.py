import requests

url = "http://localhost:8001/query"

# Test 1: General search that matches vend_search but might return 0 results (e.g. non-existent vendor)
payload1 = {
    "message": "K1 공장 존재하지않는거래처 거래처 조회",
    "limit": 50,
    "offset": 0
}

r1 = requests.post(url, json=payload1)
print("--- Test 1 (0 results) ---")
print("Response JSON:", r1.json())

# Test 2: General search that does not match any intent at all
payload2 = {
    "message": "안녕하세요 오늘 날씨 어때요?",
    "limit": 50,
    "offset": 0
}
r2 = requests.post(url, json=payload2)
print("\n--- Test 2 (No matching intent) ---")
print("Response JSON:", r2.json())
