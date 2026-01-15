"""
測試遊戲計時器功能

測試項目:
1. 計時器倒數
2. 延時功能
3. 延時次數限制
4. 超時判定
5. 對戰時長計算
"""

import requests
import time
import json

BASE_URL = "http://localhost:8001"

def test_start_game_with_timer():
    """測試帶計時器的遊戲啟動"""
    print("=" * 50)
    print("測試 1: 啟動帶計時器的遊戲 (30秒限制)")
    print("=" * 50)
    
    response = requests.post(f"{BASE_URL}/api/game/start", json={
        "mode": "nine_ball",
        "player1": "Alice",
        "player2": "Bob",
        "target_rounds": 3,
        "shot_time_limit": 30
    })
    
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["shot_time_limit"] == 30
    print("✅ 測試通過\n")


def test_timer_countdown():
    """測試計時器倒數"""
    print("=" * 50)
    print("測試 2: 計時器倒數功能")
    print("=" * 50)
    
    # 等待5秒
    print("等待 5 秒...")
    time.sleep(5)
    
    response = requests.get(f"{BASE_URL}/api/game/timer/state")
    print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    data = response.json()
    assert "remaining_time" in data
    assert data["remaining_time"] < 30  # 應該小於初始時間
    print(f"✅ 剩餘時間: {data['remaining_time']}秒\n")


def test_apply_delay():
    """測試延時功能"""
    print("=" * 50)
    print("測試 3: 延時功能 (+30秒)")
    print("=" * 50)
    
    # 獲取當前時間
    response = requests.get(f"{BASE_URL}/api/game/timer/state")
    before_time = response.json()["remaining_time"]
    print(f"延時前剩餘時間: {before_time}秒")
    
    # 應用延時
    response = requests.post(f"{BASE_URL}/api/game/timer/delay", json={
        "player": 1
    })
    
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    data = response.json()
    assert data["status"] == "delay_applied"
    assert data["remaining_time"] >= before_time + 25  # 至少增加25秒 (考慮誤差)
    assert data["delay_used"][0] == True  # P1 已用
    assert data["delay_used"][1] == False  # P2 未用
    print("✅ 測試通過\n")


def test_delay_limit():
    """測試延時次數限制"""
    print("=" * 50)
    print("測試 4: 延時次數限制 (每人每局1次)")
    print("=" * 50)
    
    # 再次嘗試延時
    response = requests.post(f"{BASE_URL}/api/game/timer/delay", json={
        "player": 1
    })
    
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 應該返回錯誤
    assert response.status_code == 200  # API 返回 200 但內容是錯誤
    data = response.json()
    assert "error_code" in data or "error" in data
    print("✅ 測試通過 (正確拒絕重複延時)\n")


def test_game_duration():
    """測試對戰時長"""
    print("=" * 50)
    print("測試 5: 對戰時長計算")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/game/state")
    print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    data = response.json()
    assert "game_duration" in data
    assert data["game_duration"] > 0  # 應該有經過時間
    print(f"✅ 對戰時長: {data['game_duration']}秒\n")


def test_timeout_detection():
    """測試超時檢測"""
    print("=" * 50)
    print("測試 6: 超時檢測 (模擬)")
    print("=" * 50)
    
    # 啟動一個很短時間限制的遊戲
    requests.post(f"{BASE_URL}/api/game/end")
    
    response = requests.post(f"{BASE_URL}/api/game/start", json={
        "mode": "nine_ball",
        "player1": "Test1",
        "player2": "Test2",
        "target_rounds": 1,
        "shot_time_limit": 3  # 3秒限制
    })
    
    print("等待超時...")
    time.sleep(4)
    
    response = requests.get(f"{BASE_URL}/api/game/timer/state")
    data = response.json()
    
    print(f"回應: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert data["remaining_time"] == 0
    assert data["is_timeout"] == True
    print("✅ 超時檢測正常\n")


if __name__ == "__main__":
    try:
        print("\n🧪 開始測試遊戲計時器功能\n")
        
        test_start_game_with_timer()
        test_timer_countdown()
        test_apply_delay()
        test_delay_limit()
        test_game_duration()
        test_timeout_detection()
        
        print("=" * 50)
        print("🎉 所有測試通過!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ 測試失敗: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ 無法連接到後端伺服器")
        print("請確認後端已啟動: python backend/main.py")
    except Exception as e:
        print(f"\n❌ 測試錯誤: {e}")
