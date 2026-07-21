import requests
import config

def ask(message: str = "", intent: str = None, fact: str = None, as_find: str = None, limit: int = 50, offset: int = 0) -> dict:
    """
    Sends a query request to the FastAPI server and returns the parsed JSON response.
    """
    url = f"{config.API_BASE_URL.rstrip('/')}/query"
    payload = {}
    
    if message:
        payload["message"] = message
    if intent:
        payload["intent"] = intent
    if fact:
        payload["fact"] = fact
    if as_find:
        payload["as_find"] = as_find
    payload["limit"] = limit
    payload["offset"] = offset
        
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "intent": "None",
                "result": [],
                "count": 0,
                "message": f"서버 오류가 발생했습니다. (HTTP {response.status_code})"
            }
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return {
            "intent": "None",
            "result": [],
            "count": 0,
            "message": "서버에 연결할 수 없습니다. 서버가 켜져 있는지 확인해 주세요."
        }

def get_selective_programs(fact: str, lang: str = "KR", idno: str = "Y6") -> list:
    """
    Fetches the authorized programs for selective query search from the API.
    """
    url = f"{config.API_BASE_URL.rstrip('/')}/selective-programs"
    payload = {
        "fact": fact,
        "lang": lang,
        "idno": idno
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch selective programs (HTTP {response.status_code})")
            return []
    except requests.exceptions.RequestException as e:
        print(f"API request for selective programs failed: {e}")
        return []
