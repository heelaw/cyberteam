# RTStream 指南

## 概述

RTStream 支持实时摄取实时视频流 (RTSP/RTMP) 和桌面捕获会话。连接后，您可以记录、索引、搜索和导出实时来源的内容。

代码级详细信息（SDK方法、参数、示例）请参见[rtstream-reference.md](rtstream-reference.md)。

## 用例

- **安全和监控**：连接 RTSP 摄像头、检测事件、触发警报
- **直播**：提取 RTMP 流，实时索引，启用即时搜索
- **会议录音**：捕获桌面屏幕和音频、实时转录、导出录音
- **事件处理**：监控实时反馈、运行人工智能分析、响应检测到的内容

## 快速入门

1. **连接到直播流** (RTSP/RTMP URL) 或从捕获会话获取 RTStream

2. **开始摄取**开始录制直播内容

3. **启动人工智能管道**进行实时索引（音频、视频、转录）

4. **通过 WebSocket 监控事件**以获取实时 AI 结果和警报

5. **完成后停止摄入**

6. **导出为视频**以进行永久存储和进一步处理

7. **搜索录音**以查找特定时刻

## RTStream 源

### 来自 RTSP/RTMP 流

直接连接到实时视频源：```python
rtstream = coll.connect_rtstream(
    url="rtmp://your-stream-server/live/stream-key",
    name="My Live Stream",
)
```### 来自捕获会话

从桌面捕获获取 RTStreams（麦克风、屏幕、系统音频）：```python
session = conn.get_capture_session(session_id)

mics = session.get_rtstream("mic")
displays = session.get_rtstream("screen")
system_audios = session.get_rtstream("system_audio")
```有关捕获会话工作流程，请参阅 [capture.md](capture.md)。

---

## 脚本

|脚本 |描述 |
|--------|-------------|
| `scripts/ws_listener.py` |用于实时 AI 结果的 WebSocket 事件监听器 |