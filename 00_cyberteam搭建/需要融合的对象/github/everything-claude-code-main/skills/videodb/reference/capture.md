# 捕捉指南

## 概述

VideoDB Capture 通过 AI 处理实现实时屏幕和音频录制。桌面捕获当前仅支持 **macOS**。

有关代码级详细信息（SDK 方法、事件结构、AI 管道），请参阅 [capture-reference.md](capture-reference.md)。

## 快速入门

1. **启动WebSocket侦听器**：`python script/ws_listener.py --clear &`
2. **运行捕获代码**（请参阅下面的完整捕获工作流程）
3. **事件写入**：`/tmp/videodb_events.jsonl`

---

## 完整的捕获工作流程

无需网络钩子或轮询。 WebSocket 传递所有事件，包括会话生命周期。

> **关键：** `CaptureClient` 必须在整个捕获期间保持运行。它运行本地记录器二进制文件，将屏幕/音频数据流式传输到 VideoDB。如果创建“CaptureClient”的 Python 进程退出，记录器二进制文件将被终止，并且捕获会静默停止。始终将捕获代码作为 **长期后台进程** 运行（例如“nohup python capture_script.py &”）并使用信号处理（“asyncio.Event”+“SIGINT”/“SIGTERM”）使其保持活动状态，直到您明确停止它。

1. **在后台启动 WebSocket 监听器**，使用 `--clear` 标志来清除旧事件。等待它创建 WebSocket ID 文件。

2. **读取 WebSocket ID**。捕获会话和 AI 管道需要此 ID。

3. **创建捕获会话**并为桌面客户端生成客户端令牌。

4. **使用令牌初始化 CaptureClient**。请求麦克风和屏幕捕获的权限。

5. **列出并选择通道**（麦克风、显示器、系统音频）。在您想要保留为视频的频道上设置“store = True”。

6. **使用选定的频道开始会话**。

7. **通过读取事件等待会话活动**，直到看到“capture_session.active”。该事件包含“rtstreams”数组。将会话信息（会话 ID、RTStream ID）保存到文件（例如“/tmp/videodb_capture_info.json”），以便其他脚本可以读取它。

8. **保持进程处于活动状态。** 将 `asyncio.Event` 与 `SIGINT`/`SIGTERM` 的信号处理程序一起使用，以阻止直到显式停止。写入 PID 文件（例如 `/tmp/videodb_capture_pid`），以便稍后可以使用 `kill $(cat /tmp/videodb_capture_pid)` 停止该进程。每次运行时都应覆盖 PID 文件，以便重新运行时始终具有正确的 PID。

9. **在每个 RTStream 上启动 AI 管道**（在单独的命令/脚本中）以进行音频索引和视觉索引。从保存的会话信息文件中读取 RTStream ID。

10. **编写自定义事件处理逻辑**（在单独的命令/脚本中）以根据您的用例读取实时事件。示例：
    - 当“visual_index”提到“Slack”时记录 Slack 活动
    - 总结“audio_index”事件到达时的讨论
    - 当特定关键字出现在“成绩单”中时触发警报
    - 从屏幕描述跟踪应用程序的使用情况

11. **完成后停止捕获** — 向捕获进程发送 SIGTERM。它应该在其信号处理程序中调用“client.stop_capture()”和“client.shutdown()”。

12. **通过读取事件等待导出**，直到看到“capture_session.exported”。此事件包含“exported_video_id”、“stream_url”和“player_url”。停止捕获后这可能需要几秒钟的时间。

13. **收到导出事件后停止WebSocket侦听器**。使用“kill $(cat /tmp/videodb_ws_pid)”来彻底终止它。

---

## 关闭顺序

正确的关闭顺序对于确保捕获所有事件非常重要：

1. **停止捕获会话** — `client.stop_capture()` 然后 `client.shutdown()`
2. **等待导出事件** — 轮询“/tmp/videodb_events.jsonl”以获取“capture_session.exported”
3. **停止 WebSocket 监听器** — `kill $(cat /tmp/videodb_ws_pid)`

在收到导出事件之前，请勿终止 WebSocket 侦听器，否则您将错过最终的视频 URL。

---

## 脚本

|脚本 |描述 |
|--------|-------------|
| `scripts/ws_listener.py` | WebSocket 事件侦听器（转储到 JSONL）|

### ws_listener.py 用法```bash
# Start listener in background (append to existing events)
python scripts/ws_listener.py &

# Start listener with clear (new session, clears old events)
python scripts/ws_listener.py --clear &

# Custom output directory
python scripts/ws_listener.py --clear /path/to/events &

# Stop the listener
kill $(cat /tmp/videodb_ws_pid)
```**选项：**
- `--clear`：开始前清除事件文件。开始新的捕获会话时使用。

**输出文件：**
- `videodb_events.jsonl` - 所有 WebSocket 事件
- `videodb_ws_id` - WebSocket 连接 ID（对于 `ws_connection_id` 参数）
- `videodb_ws_pid` - 进程 ID（用于停止监听器）

**特点：**
- 连接断开时自动重新连接并具有指数退避功能
- SIGINT/SIGTERM 时正常关闭
- PID文件，方便进程管理
- 连接状态记录