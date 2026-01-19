"""
錄影管理器 - 處理遊戲錄影和事件記錄

遵照 v1.5 技術指南:
- 錄製後端合成的 burn-in 串流
- 記錄遊戲事件時間軸
- 檔案結構化儲存
- 預留回放分析接口
- 自動同步至資料庫
"""

import os
import json
import cv2
import time
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
import threading

# 導入資料庫
from database import Database


@dataclass
class RecordingMetadata:
    """錄影元資料"""
    game_id: str
    game_type: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: float = 0
    players: Optional[List[str]] = None
    final_score: Optional[List[int]] = None
    winner: Optional[str] = None
    total_rounds: int = 0
    video_resolution: str = "1280x720"
    video_fps: int = 30
    file_size_mb: float = 0


class RecordingManager:
    """遊戲錄影管理器"""
    
    def __init__(self, recordings_dir: str = "./recordings", db_path: str = "./data/recordings.db"):
        """
        初始化錄影管理器
        
        Args:
            recordings_dir: 錄影檔案儲存目錄
            db_path: 資料庫路徑
        """
        self.recordings_dir = recordings_dir
        os.makedirs(recordings_dir, exist_ok=True)
        
        # 初始化資料庫連接
        self.db = Database(db_path)
        
        self.current_recording: Optional[Dict[str, Any]] = None
        self.video_writer: Optional[cv2.VideoWriter] = None
        self.events_file: Optional[Any] = None
        self.recording_lock = threading.Lock()
    
    def start_recording(
        self, 
        game_type: str,
        players: Optional[List[str]] = None,
        resolution: tuple = (1280, 720),
        fps: int = 30
    ) -> str:
        """
        開始錄影
        
        Args:
            game_type: 遊戲類型 ("nine_ball", "practice_single", etc.)
            players: 玩家名單 (可選)
            resolution: 影片解析度
            fps: 影片幀率
        
        Returns:
            game_id: 遊戲ID
        
        Raises:
            RuntimeError: 如果已經在錄影中
        """
        with self.recording_lock:
            if self.current_recording:
                raise RuntimeError("Already recording")
            
            # 生成遊戲 ID (時間戳)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            game_id = f"game_{timestamp}"
            
            # 建立錄影目錄
            recording_dir = os.path.join(self.recordings_dir, game_id)
            os.makedirs(recording_dir, exist_ok=True)
            
            # 初始化影片寫入（使用 mp4v 格式，兼容性更好）
            video_path = os.path.join(recording_dir, "video.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 使用 mp4v 編碼（廣泛支援）
            self.video_writer = cv2.VideoWriter(
                video_path, fourcc, fps, resolution
            )
            
            if not self.video_writer.isOpened():
                raise RuntimeError(f"Failed to open video writer: {video_path}")
            
            # 初始化事件日誌
            events_path = os.path.join(recording_dir, "events.jsonl")
            self.events_file = open(events_path, 'w', encoding='utf-8')
            
            # 記錄元資料
            metadata = RecordingMetadata(
                game_id=game_id,
                game_type=game_type,
                start_time=datetime.now().isoformat(),
                players=players or [],
                video_resolution=f"{resolution[0]}x{resolution[1]}",
                video_fps=fps
            )
            
            self.current_recording = {
                "game_id": game_id,
                "recording_dir": recording_dir,
                "metadata": metadata,
                "start_time": time.time(),
                "frame_count": 0
            }
            
            # 記錄開始事件
            self._log_event("game_start", {
                "game_type": game_type,
                "players": players or []
            })
            
            print(f"[Recording] Started: {game_id}")
            return game_id
    
    def write_frame(self, frame) -> bool:
        """
        寫入一幀影像
        
        Args:
            frame: OpenCV 影像 (numpy array)
        
        Returns:
            是否成功寫入
        """
        with self.recording_lock:
            if not self.current_recording or not self.video_writer:
                return False
            
            try:
                self.video_writer.write(frame)
                self.current_recording["frame_count"] += 1
                return True
            except Exception as e:
                print(f"[Recording] Frame write error: {e}")
                return False
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """
        記錄遊戲事件
        
        Args:
            event_type: 事件類型
            data: 事件數據
        """
        self._log_event(event_type, data)
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """內部事件記錄方法"""
        if not self.events_file:
            return
        
        event = {
            "timestamp": time.time(),
            "event": event_type,
            "data": data
        }
        
        try:
            self.events_file.write(json.dumps(event, ensure_ascii=False) + '\n')
            self.events_file.flush()
        except Exception as e:
            print(f"[Recording] Event log error: {e}")
    
    def stop_recording(
        self,
        final_score: Optional[List[int]] = None,
        winner: Optional[str] = None,
        total_rounds: int = 0
    ) -> Dict[str, Any]:
        """
        停止錄影並保存
        
        Args:
            final_score: 最終比分
            winner: 勝者
            total_rounds: 總回合數
        
        Returns:
            錄影資訊
        
        Raises:
            RuntimeError: 如果沒有活動的錄影
        """
        with self.recording_lock:
            if not self.current_recording:
                raise RuntimeError("No active recording")
            
            # 記錄結束事件
            self._log_event("game_end", {
                "winner": winner,
                "final_score": final_score,
                "total_rounds": total_rounds
            })
            
            # 關閉檔案
            if self.video_writer:
                self.video_writer.release()
            if self.events_file:
                self.events_file.close()
            
            # 更新元資料
            metadata = self.current_recording["metadata"]
            metadata.end_time = datetime.now().isoformat()
            metadata.duration_seconds = time.time() - self.current_recording["start_time"]
            metadata.final_score = final_score
            metadata.winner = winner
            metadata.total_rounds = total_rounds
            
            # 計算檔案大小
            video_path = os.path.join(
                self.current_recording["recording_dir"], "video.mp4"
            )
            if os.path.exists(video_path):
                file_size_bytes = os.path.getsize(video_path)
                metadata.file_size_mb = file_size_bytes / (1024 * 1024)
                
                # 生成縮圖（提取第一幀）
                try:
                    cap = cv2.VideoCapture(video_path)
                    ret, frame = cap.read()
                    if ret:
                        thumbnail_path = os.path.join(
                            self.current_recording["recording_dir"], "thumbnail.jpg"
                        )
                        # 調整大小為 640x360 以節省空間
                        thumbnail = cv2.resize(frame, (640, 360))
                        cv2.imwrite(thumbnail_path, thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        print(f"[Recording] Thumbnail generated: {thumbnail_path}")
                    cap.release()
                except Exception as e:
                    print(f"[Recording] Thumbnail generation error: {e}")
            
            # 保存元資料
            metadata_path = os.path.join(
                self.current_recording["recording_dir"], "metadata.json"
            )
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(metadata), f, indent=2, ensure_ascii=False)
            
            #  同步至資料庫
            try:
                video_path = os.path.join(
                    self.current_recording["recording_dir"], "video.mp4"
                )
                
                # 準備資料庫記錄
                recording_data = {
                    "game_id": metadata.game_id,
                    "game_type": metadata.game_type,
                    "start_time": metadata.start_time,
                    "end_time": metadata.end_time,
                    "duration_seconds": metadata.duration_seconds,
                    "player1_name": metadata.players[0] if metadata.players and len(metadata.players) > 0 else None,
                    "player2_name": metadata.players[1] if metadata.players and len(metadata.players) > 1 else None,
                    "winner": metadata.winner,
                    "player1_score": metadata.final_score[0] if metadata.final_score and len(metadata.final_score) > 0 else 0,
                    "player2_score": metadata.final_score[1] if metadata.final_score and len(metadata.final_score) > 1 else 0,
                    "target_rounds": metadata.total_rounds,
                    "video_path": video_path,
                    "video_resolution": metadata.video_resolution,
                    "video_fps": metadata.video_fps,
                    "file_size_mb": metadata.file_size_mb
                }
                
                self.db.insert_recording(recording_data)
                print(f"[Recording] Synced to database: {metadata.game_id}")
            except Exception as e:
                print(f"[Recording] Database sync error: {e}")
            
            result = {
                "game_id": self.current_recording["game_id"],
                "duration": metadata.duration_seconds,
                "frame_count": self.current_recording["frame_count"],
                "file_size_mb": round(metadata.file_size_mb, 2)
            }
            
            print(f"[Recording] Stopped: {result}")
            
            # 清理狀態
            self.current_recording = None
            self.video_writer = None
            self.events_file = None
            
            return result
    
    def get_recordings_list(self) -> List[Dict[str, Any]]:
        """
        獲取所有錄影列表
        
        Returns:
            錄影元資料列表 (按時間排序,最新在前)
        """
        recordings = []
        
        if not os.path.exists(self.recordings_dir):
            return recordings
        
        try:
            for game_dir in os.listdir(self.recordings_dir):
                metadata_path = os.path.join(
                    self.recordings_dir, game_dir, "metadata.json"
                )
                
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        recordings.append(metadata)
        except Exception as e:
            print(f"[Recording] List error: {e}")
        
        # 按時間排序 (最新在前)
        recordings.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        return recordings
    
    def get_recording_metadata(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取特定錄影的元資料
        
        Args:
            game_id: 遊戲ID
        
        Returns:
            元資料字典,若不存在則返回None
        """
        metadata_path = os.path.join(
            self.recordings_dir, game_id, "metadata.json"
        )
        
        if not os.path.exists(metadata_path):
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Recording] Metadata read error: {e}")
            return None
    
    def get_recording_events(self, game_id: str) -> List[Dict[str, Any]]:
        """
        獲取錄影的事件日誌
        
        Args:
            game_id: 遊戲ID
        
        Returns:
            事件列表
        """
        events_path = os.path.join(
            self.recordings_dir, game_id, "events.jsonl"
        )
        
        if not os.path.exists(events_path):
            return []
        
        events = []
        try:
            with open(events_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))
        except Exception as e:
            print(f"[Recording] Events read error: {e}")
        
        return events
    
    @property
    def is_recording(self) -> bool:
        """檢查是否正在錄影"""
        return self.current_recording is not None
