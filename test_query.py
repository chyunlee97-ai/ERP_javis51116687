import sys
import os

# Add server path to path
sys.path.append(os.path.join(os.path.dirname(__file__), "server"))

from routers.query import QueryRequest, handle_query

req = QueryRequest(
    message="광저우D 법인장 내선",
    fact="K1"
)

res = handle_query(req)
print(f"Intent: {res.intent}")
print(f"Query Script: {res.query_script}")
print(f"Results Count: {res.count}")
