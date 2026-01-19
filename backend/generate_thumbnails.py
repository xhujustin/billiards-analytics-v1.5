"""
為舊錄影批次生成縮圖

這個腳本會掃描所有錄影資料夾，為沒有縮圖的錄影生成縮圖
"""
import os
import cv2

recordings_dir = "./recordings"

# 掃描所有錄影資料夾
for game_id in os.listdir(recordings_dir):
    game_dir = os.path.join(recordings_dir, game_id)
    
    if not os.path.isdir(game_dir):
        continue
    
    video_path = os.path.join(game_dir, "video.mp4")
    thumbnail_path = os.path.join(game_dir, "thumbnail.jpg")
    
    # 如果已有縮圖，跳過
    if os.path.exists(thumbnail_path):
        print(f"✓ {game_id}: 縮圖已存在")
        continue
    
    # 如果沒有影片檔案，跳過
    if not os.path.exists(video_path):
        print(f"✗ {game_id}: 影片檔案不存在")
        continue
    
    # 生成縮圖
    try:
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        
        if ret:
            # 調整大小為 640x360
            thumbnail = cv2.resize(frame, (640, 360))
            cv2.imwrite(thumbnail_path, thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 85])
            print(f"✓ {game_id}: 縮圖已生成")
        else:
            print(f"✗ {game_id}: 無法讀取影片第一幀")
        
        cap.release()
    except Exception as e:
        print(f"✗ {game_id}: 錯誤 - {e}")

print("\n完成！")
