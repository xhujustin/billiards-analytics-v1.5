"""
測試 OpenCV H.264 編碼器支援
"""
import cv2
import numpy as np

print("測試 H.264 編碼器...")

# 創建測試影像
test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)

# 測試不同的編碼器
codecs = [
    ('H264', cv2.VideoWriter_fourcc(*'H264')),
    ('X264', cv2.VideoWriter_fourcc(*'X264')),
    ('mp4v', cv2.VideoWriter_fourcc(*'mp4v')),
    ('avc1', cv2.VideoWriter_fourcc(*'avc1')),
]

for name, fourcc in codecs:
    try:
        writer = cv2.VideoWriter(
            f'test_{name}.mp4',
            fourcc,
            30,
            (1280, 720)
        )
        
        if writer.isOpened():
            print(f"✅ {name}: 支援")
            writer.write(test_frame)
            writer.release()
        else:
            print(f"❌ {name}: 不支援（無法開啟）")
    except Exception as e:
        print(f"❌ {name}: 錯誤 - {e}")

print("\n建議：如果 H264 不支援，請使用 mp4v 或 X264")
