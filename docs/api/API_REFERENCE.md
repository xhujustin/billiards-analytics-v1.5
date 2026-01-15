# API_REFERENCE.md
## 撞球分析系統 API 參考（v1.5）

本文件僅包含 **REST API / WebSocket 協議 / Schema**，作為前後端對接的權威來源。

---

## REST API

### Streams
- GET /api/streams
- GET /api/stream/status

### Sessions
- POST /api/sessions
- POST /api/sessions/{session_id}/renew
- POST /api/sessions/{session_id}/switch_stream
- DELETE /api/sessions/{session_id}

### Config
- GET /api/config

### Control (v1.5 擴充)
- POST /api/control/toggle - 啟用/停用 YOLO 辨識
- POST /api/control/snapshot - 截圖功能
- POST /api/stream/quality - 設定串流品質 (low/med/high/auto)

### Performance (v1.5 新增)
- GET /api/performance/stats - 獲取即時效能統計 (FPS, 延遲)

### Game Mode (v1.5 新增)
- POST /api/game/start - 開始遊戲 (9球)
- POST /api/game/check_rules - 檢查規則
- POST /api/game/end_turn - 結束回合
- GET /api/game/state - 獲取遊戲狀態
- POST /api/game/end - 結束遊戲

### Practice Mode (v1.5 新增)
- POST /api/practice/start - 開始練習
- POST /api/practice/record - 記錄結果
- GET /api/practice/state - 獲取練習狀態
- POST /api/practice/end - 結束練習

### Recording (v1.5 新增)
- POST /api/recording/start - 開始錄影
- POST /api/recording/stop - 停止錄影
- POST /api/recording/event - 記錄事件
- GET /api/recordings - 錄影列表
- GET /api/recording/{id}/metadata - 錄影元資料
- GET /api/recording/{id}/events - 錄影事件

### Game Timer (v1.5 新增)
- GET /api/game/timer/state - 獲取計時器狀態
- POST /api/game/timer/delay - 應用延時 (+30秒)

### Replay
- GET /api/recordings
- GET /replay/burnin/{recording_id}.mjpg
- GET /replay/events/{recording_id}

---

## WebSocket

### Endpoint
- WS /ws/control?session_id=...

### Message Types
- heartbeat
- client.heartbeat
- metadata.update
- stream.changed / stream.changed.ack
- session.revoked
- cmd.* / cmd.ack / cmd.error
- protocol.hello / protocol.welcome

---

## Schema（摘要）
請參考 IMPLEMENTATION_GUIDE.md 中的 TypeScript 定義作為實作依據。