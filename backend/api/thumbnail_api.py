"""
縮圖 API - 提供錄影縮圖圖片
"""
from fastapi import APIRouter, Response
import os

router = APIRouter()

@router.get("/api/recordings/{game_id}/thumbnail")
async def get_thumbnail(game_id: str):
    """
    獲取錄影縮圖
    """
    # 使用絕對路徑
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    thumbnail_path = os.path.join(project_root, "recordings", game_id, "thumbnail.jpg")
    
    if not os.path.exists(thumbnail_path):
        # 如果縮圖不存在，返回 404
        return Response(status_code=404)
    
    # 讀取並返回縮圖
    with open(thumbnail_path, "rb") as f:
        return Response(content=f.read(), media_type="image/jpeg")

