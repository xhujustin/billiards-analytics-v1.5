"""
攝像頭控制 API 模組

提供攝像頭列舉和切換功能
改用 PowerShell 列舉設備，避免 OpenCV VCamDShow 錯誤
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
import cv2
import asyncio
import subprocess
import re

router = APIRouter()

# Global variables shared from main.py
camera_state = None
switch_camera_func = None

def init_camera_api(main_module):
    """初始化 API 模組，取得 main 模組的共享變數"""
    global camera_state, switch_camera_func
    camera_state = main_module.camera_state
    switch_camera_func = main_module.switch_camera_background

def get_connected_cameras_windows():
    """
    使用 PowerShell 列舉 Windows 上的攝像頭設備名稱。
    這避免了使用 OpenCV 暴力掃描導致的 VCamDShow 錯誤。
    """
    cameras = []
    try:
        # 使用 PowerShell 獲取 PNPClass 為 Camera 或 Image 的設備
        # 這比 wmic 更可靠，能過濾掉許多虛擬設備
        cmd = [
            "powershell",
            "-Command",
            "Get-PnpDevice -Class Camera,Image -Status OK | Select-Object -ExpandProperty FriendlyName"
        ]
        
        # 執行命令，並強制使用 utf-8 解碼以支援中文名稱
        # 注意：某些 Windows 環境可能需要特定的 codepage (如 'cp950' 或 'mbcs')，
        # 但現代 PowerShell 通常輸出 utf-8 或系統默認編碼。
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        except UnicodeDecodeError:
            # 如果 utf-8 失敗，嘗試系統默認編碼
            result = subprocess.run(cmd, capture_output=True, text=True) # 使用 default locale
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                name = line.strip()
                if name:
                    cameras.append(name)
                    
    except Exception as e:
        print(f"Error enumerating cameras via PowerShell: {e}")
        # 如果失敗，回退到空列表
        return []

    return cameras

@router.get("/api/camera/list")
async def list_cameras():
    """列出可用攝像頭"""
    available_cameras = []
    current_id = camera_state.get("selected_device_id", 0)
    
    # 1. 獲取系統中的真實攝像頭列表 (不會報錯!)
    camera_names = get_connected_cameras_windows()
    
    # 2. 構建列表
    # 注意: PowerShell 返回的順序通常對應 OpenCV 的 Index 順序
    if camera_names:
        for i, name in enumerate(camera_names):
            available_cameras.append({
                "id": i, 
                "name": f"{name} (Camera {i})" 
            })
    else:
        # 如果 PowerShell 失敗，至少回傳當前使用的和基礎的 0, 1
        available_cameras.append({"id": current_id, "name": f"Camera {current_id} (Data Only)"})
        if current_id != 0:
             available_cameras.append({"id": 0, "name": "Camera 0 (Possible)"})
        if current_id != 1:
             available_cameras.append({"id": 1, "name": "Camera 1 (Possible)"})
        
        available_cameras.sort(key=lambda x: x["id"])

    return {
        "cameras": available_cameras,
        "current": current_id,
        "is_switching": camera_state.get("is_switching", False)
    }

@router.post("/api/camera/switch")
async def switch_camera(data: dict, background_tasks: BackgroundTasks):
    """切換攝像頭 (非同步)"""
    device_id = data.get("device_id")
    if device_id is None:
        raise HTTPException(status_code=400, detail="Device ID required")
        
    if camera_state.get("is_switching", False):
         raise HTTPException(status_code=400, detail="Camera is currently switching")

    if camera_state.get("selected_device_id") == device_id:
        return {"status": "ok", "message": "Already on this camera"}

    # 標記為正在切換
    camera_state["is_switching"] = True
    
    # 在背景執行切換，避免阻塞 API
    background_tasks.add_task(switch_camera_func, device_id)
    
    return {"status": "ok", "message": f"Switching to camera {device_id}..."}
