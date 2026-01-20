import requests

game_id = "game_20260119_225848"
url = f"http://localhost:8001/api/recordings/{game_id}/video"

print(f"測試影片 API: {url}\n")

try:
    response = requests.get(url, stream=True)
    print(f"狀態碼: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Length: {response.headers.get('Content-Length')}")
    
    if response.status_code == 200:
        print("\n影片 API 正常！")
    else:
        print(f"\n錯誤：{response.text}")
except Exception as e:
    print(f"\n錯誤：{e}")
