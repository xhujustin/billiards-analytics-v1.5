"""
檢查影片編碼格式
"""
import cv2
import os

video_path = r"C:\Users\YiFang\OneDrive\桌面\billiards-analytics-v1.5\recordings\game_20260119_225848\video.mp4"

if os.path.exists(video_path):
    cap = cv2.VideoCapture(video_path)
    
    # 獲取影片資訊
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # 轉換 fourcc 為可讀格式
    fourcc_str = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
    
    print(f"影片路徑: {video_path}")
    print(f"編碼格式: {fourcc_str}")
    print(f"FPS: {fps}")
    print(f"解析度: {width}x{height}")
    print(f"總幀數: {frame_count}")
    
    # 測試是否能讀取第一幀
    ret, frame = cap.read()
    if ret:
        print(f"\n可以讀取影片內容")
    else:
        print(f"\n無法讀取影片內容！")
    
    cap.release()
    
    print(f"\n========== 診斷 ==========")
    if fourcc_str in ['mp4v', 'MP4V']:
        print("問題：mp4v 編碼不被大多數瀏覽器支援")
        print("解決方案：需要使用 H.264 (avc1) 編碼")
    elif fourcc_str in ['avc1', 'h264', 'H264']:
        print("編碼格式正確：H.264")
    else:
        print(f"未知編碼格式：{fourcc_str}")
else:
    print(f"影片檔案不存在: {video_path}")
