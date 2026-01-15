"""
測試遊戲啟動 API
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_game_start():
    """測試遊戲啟動"""
    print("=" * 50)
    print("測試遊戲啟動 API")
    print("=" * 50)
    
    response = requests.post(f"{BASE_URL}/api/game/start", json={
        "mode": "nine_ball",
        "player1": "測試玩家1",
        "player2": "測試玩家2",
        "target_rounds": 3,
        "shot_time_limit": 0
    })
    
    print(f"狀態碼: {response.status_code}")
    print(f"回應內容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        data = response.json()
        if "status" in data:
            print("✅ 遊戲啟動成功!")
        else:
            print("⚠️ 回應格式異常")
    else:
        print("❌ 遊戲啟動失敗")

if __name__ == "__main__":
    try:
        test_game_start()
    except requests.exceptions.ConnectionError:
        print("\n❌ 無法連接到後端")
        print("請確認後端已啟動: python backend/main.py")
    except Exception as e:
        print(f"\n❌ 測試錯誤: {e}")
