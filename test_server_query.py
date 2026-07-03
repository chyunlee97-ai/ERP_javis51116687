import sys
import os

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "server"))

from services import intent_matcher, db_service

print("Loading intents...")
intents = intent_matcher.load_intents()
print("Intents count:", len(intents))

intent_item = None
for item in intents:
    if item.get("intent") == "vend_search":
        intent_item = item
        break

if not intent_item:
    print("Error: vend_search intent not found!")
    sys.exit(1)

query = intent_item.get("query")
print("Query in memory:\n", repr(query))

# Execute query
params = ["K1", "LG"]
print("\nExecuting query via db_service.execute_query...")
try:
    results = db_service.execute_query(query, params)
    print("Success! Results count:", len(results))
    if results:
        print("First result:", results[0])
except Exception as e:
    print("Error in execution:", e)
