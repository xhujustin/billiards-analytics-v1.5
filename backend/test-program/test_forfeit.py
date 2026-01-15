"""
測試認輸 API
"""
import requests
import json

response = requests.post("http://localhost:8001/api/game/forfeit", json={
    "forfeit_player": 1
})

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
