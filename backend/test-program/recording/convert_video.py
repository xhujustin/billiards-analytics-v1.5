"""
將 mp4v 編碼的影片轉換為 H.264 編碼

這個腳本會使用 ffmpeg 轉換影片為瀏覽器支援的 H.264 編碼
需要先安裝 ffmpeg: https://ffmpeg.org/download.html
"""
import os
import subprocess

video_path = r"C:\Users\YiFang\OneDrive\桌面\billiards-analytics-v1.5\recordings\game_20260119_225848\video.mp4"
output_path = r"C:\Users\YiFang\OneDrive\桌面\billiards-analytics-v1.5\recordings\game_20260119_225848\video_h264.mp4"

if not os.path.exists(video_path):
    print(f"影片檔案不存在: {video_path}")
    exit(1)

print(f"正在轉換影片為 H.264 編碼...")
print(f"來源: {video_path}")
print(f"目標: {output_path}")

try:
    # 使用 ffmpeg 轉換
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-c:v', 'libx264',  # H.264 編碼
        '-preset', 'fast',
        '-crf', '23',
        '-c:a', 'aac',  # 音訊編碼
        '-y',  # 覆蓋輸出檔案
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"\n轉換成功！")
        print(f"輸出檔案: {output_path}")
        
        # 取代原檔案
        if input("\n是否要取代原影片檔案？(y/n): ").lower() == 'y':
            os.remove(video_path)
            os.rename(output_path, video_path)
            print(f"已取代原檔案")
    else:
        print(f"\n轉換失敗:")
        print(result.stderr)
        
except FileNotFoundError:
    print("\n錯誤：找不到 ffmpeg")
    print("請先安裝 ffmpeg: https://ffmpeg.org/download.html")
    print("或使用: winget install ffmpeg")
