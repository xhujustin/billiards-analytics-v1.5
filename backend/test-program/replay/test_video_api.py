"""
測試影片 API 是否正常
"""
import requests

game_id = "game_20260120_154043"
url = f"http://localhost:8001/api/recordings/{game_id}/video"

print(f"測試 URL: {url}\n")

try:
    # 不帶 Range 的請求
    print("1. 測試完整影片請求...")
    response = requests.get(url, stream=True)
    print(f"   狀態碼: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type')}")
    print(f"   Content-Length: {response.headers.get('Content-Length')}")
    print(f"   Accept-Ranges: {response.headers.get('Accept-Ranges')}")
    
    # 帶 Range 的請求
    print("\n2. 測試範圍請求...")
    response = requests.get(url, headers={"Range": "bytes=0-1023"}, stream=True)
    print(f"   狀態碼: {response.status_code}")
    print(f"   Content-Range: {response.headers.get('Content-Range')}")
    print(f"   Content-Length: {response.headers.get('Content-Length')}")
    
    if response.status_code in [200, 206]:
        print("\n✓ API 正常運作")
    else:
        print(f"\n✗ API 錯誤: {response.text[:200]}")
        
except Exception as e:
    print(f"\n✗ 連接錯誤: {e}")
