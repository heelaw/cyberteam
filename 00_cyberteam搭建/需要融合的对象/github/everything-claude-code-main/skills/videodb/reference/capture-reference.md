# 捕获参考

VideoDB 捕获会话的代码级详细信息。有关工作流程指南，请参阅 [capture.md](capture.md)。

---

## WebSocket 事件

来自捕获会话和 AI 管道的实时事件。无需网络钩子或轮询。

使用 [scripts/ws_listener.py](../scripts/ws_listener.py) 连接事件并将其转储到 `${VIDEODB_EVENTS_DIR:-$HOME/.local/state/videodb}/videodb_events.jsonl`。

### 事件通道

|频道|来源 |内容 |
|--------|--------|---------|
| `捕获会话` |会话生命周期 |状态变更 |
| `成绩单` | `start_transcript()` |语音转文字 |
| `视觉索引` / `场景索引` | `index_visuals()` |视觉分析|
| `音频索引` | `index_audio()` |音频分析 |
| `警报` | `create_alert()` |警报通知 |

### 会话生命周期事件

|活动 |状态 |关键数据|
|--------|--------|----------|
| `capture_session.created` | `创建` | — |
| `capture_session.starting` | `开始` | — |
| `capture_session.active` | `活跃` | `rtstreams[]` |
| `capture_session.stopping` | `停止` | — |
| `capture_session.stopped` | `停止` | — |
| `capture_session.exported` | `导出` | `exported_video_id`、`stream_url`、`player_url` |
| `capture_session.failed` | `失败` | `错误` |

### 事件结构

**事件记录：**```json
{
  "channel": "transcript",
  "rtstream_id": "rts-xxx",
  "rtstream_name": "mic:default",
  "data": {
    "text": "Let's schedule the meeting for Thursday",
    "is_final": true,
    "start": 1710000001234,
    "end": 1710000002345
  }
}
```**视觉索引事件：**```json
{
  "channel": "visual_index",
  "rtstream_id": "rts-xxx",
  "rtstream_name": "display:1",
  "data": {
    "text": "User is viewing a Slack conversation with 3 unread messages",
    "start": 1710000012340,
    "end": 1710000018900
  }
}
```**音频索引事件：**```json
{
  "channel": "audio_index",
  "rtstream_id": "rts-xxx",
  "rtstream_name": "mic:default",
  "data": {
    "text": "Discussion about scheduling a team meeting",
    "start": 1710000021500,
    "end": 1710000029200
  }
}
```**会话活动事件：**```json
{
  "event": "capture_session.active",
  "capture_session_id": "cap-xxx",
  "status": "active",
  "data": {
    "rtstreams": [
      { "rtstream_id": "rts-1", "name": "mic:default", "media_types": ["audio"] },
      { "rtstream_id": "rts-2", "name": "system_audio:default", "media_types": ["audio"] },
      { "rtstream_id": "rts-3", "name": "display:1", "media_types": ["video"] }
    ]
  }
}
```**会话导出事件：**```json
{
  "event": "capture_session.exported",
  "capture_session_id": "cap-xxx",
  "status": "exported",
  "data": {
    "exported_video_id": "v_xyz789",
    "stream_url": "https://stream.videodb.io/...",
    "player_url": "https://console.videodb.io/player?url=..."
  }
}
```> 有关最新详细信息，请参阅 [VideoDB 实时上下文文档](https://docs.videodb.io/pages/ingest/capture-sdks/realtime-context.md)。

---

## 事件持久化

使用 ws_listener.py 将所有 WebSocket 事件转储到 JSONL 文件以供以后分析。

### 启动监听器并获取WebSocket ID```bash
# Start with --clear to clear old events (recommended for new sessions)
python scripts/ws_listener.py --clear &

# Append to existing events (for reconnects)
python scripts/ws_listener.py &
```或者指定自定义输出目录：```bash
python scripts/ws_listener.py --clear /path/to/output &
# Or via environment variable:
VIDEODB_EVENTS_DIR=/path/to/output python scripts/ws_listener.py --clear &
```该脚本在第一行输出“WS_ID=<connection_id>”，然后无限期监听。

**获取ws_id：**```bash
cat "${VIDEODB_EVENTS_DIR:-$HOME/.local/state/videodb}/videodb_ws_id"
```**停止监听器：**```bash
kill "$(cat "${VIDEODB_EVENTS_DIR:-$HOME/.local/state/videodb}/videodb_ws_pid")"
```**接受`ws_connection_id`的函数：**

|功能|目的|
|----------|---------|
| `conn.create_capture_session()` |会话生命周期事件 |
| RTStream 方法 |请参阅 [rtstream-reference.md](rtstream-reference.md) |

**输出文件**（在输出目录中，默认 `${XDG_STATE_HOME:-$HOME/.local/state}/videodb`）：
- `videodb_ws_id` - WebSocket 连接 ID
- `videodb_events.jsonl` - 所有事件
- `videodb_ws_pid` - 用于轻松终止的进程 ID

**特点：**
- `--clear` 标志用于在启动时清除事件文件（用于新会话）
- 连接断开时自动重新连接并具有指数退避功能
- SIGINT/SIGTERM 时正常关闭
- 连接状态记录

### JSONL 格式

每行都是一个带有添加时间戳的 JSON 对象：```json
{"ts": "2026-03-02T10:15:30.123Z", "unix_ts": 1772446530.123, "channel": "visual_index", "data": {"text": "..."}}
{"ts": "2026-03-02T10:15:31.456Z", "unix_ts": 1772446531.456, "event": "capture_session.active", "capture_session_id": "cap-xxx"}
```### 读书活动```python
import json
import time
from pathlib import Path

events_path = Path.home() / ".local" / "state" / "videodb" / "videodb_events.jsonl"
transcripts = []
recent = []
visual = []

cutoff = time.time() - 600
with events_path.open(encoding="utf-8") as handle:
    for line in handle:
        event = json.loads(line)
        if event.get("channel") == "transcript":
            transcripts.append(event)
        if event.get("unix_ts", 0) > cutoff:
            recent.append(event)
        if (
            event.get("channel") == "visual_index"
            and "code" in event.get("data", {}).get("text", "").lower()
        ):
            visual.append(event)
```---

## WebSocket 连接

连接以接收来自转录和索引管道的实时 AI 结果。```python
ws_wrapper = conn.connect_websocket()
ws = await ws_wrapper.connect()
ws_id = ws.connection_id
```|属性/方法|类型 |描述 |
|--------------------|------|-------------|
| `ws.connection_id` | `str` |唯一的连接 ID（传递给 AI 管道方法）|
| `ws.receive()` | `AsyncIterator[dict]` |异步迭代器产生实时消息 |

---

## 捕获会话

### 连接方法

|方法|返回|描述 |
|--------|---------|-------------|
| `conn.create_capture_session（end_user_id，collection_id，ws_connection_id，元数据）` | `捕获会话` |创建新的捕获会话 |
| `conn.get_capture_session(capture_session_id)` | `捕获会话` |检索现有的捕获会话 |
| `conn.generate_client_token()` | `str` |生成客户端身份验证令牌 |

### 创建捕获会话```python
from pathlib import Path

ws_id = (Path.home() / ".local" / "state" / "videodb" / "videodb_ws_id").read_text().strip()

session = conn.create_capture_session(
    end_user_id="user-123",  # required
    collection_id="default",
    ws_connection_id=ws_id,
    metadata={"app": "my-app"},
)
print(f"Session ID: {session.id}")
```> **注意：** `end_user_id` 是必需的，用于标识发起捕获的用户。出于测试或演示目的，任何唯一的字符串标识符都可以（例如“demo-user”、“test-123”）。

### CaptureSession 属性

|物业 |类型 |描述 |
|----------|------|-------------|
| `session.id` | `str` |唯一的捕获会话 ID |

### CaptureSession 方法

|方法|返回|描述 |
|--------|---------|-------------|
| `session.get_rtstream(类型)` | `列表[RTStream]` |按类型获取 RTStream：`"mic"`、`"screen"` 或 `"system_audio"` |

### 生成客户端令牌```python
token = conn.generate_client_token()
```---

## 捕获客户端

客户端在用户的计算机上运行并处理权限、频道发现和流式传输。```python
from videodb.capture import CaptureClient

client = CaptureClient(client_token=token)
```### CaptureClient 方法

|方法|返回|描述 |
|--------|---------|-------------|
| `等待 client.request_permission(type)` | `无` |请求设备权限（“麦克风”、“屏幕捕获”）|
| `等待 client.list_channels()` | `渠道` |发现可用的音频/视频频道 |
| `等待 client.start_capture_session（capture_session_id，频道，primary_video_channel_id）` | `无` |开始播放选定的频道 |
| `等待 client.stop_capture()` | `无` |优雅地停止捕获会话 |
| `等待 client.shutdown()` | `无` |清理客户资源|

### 请求权限```python
await client.request_permission("microphone")
await client.request_permission("screen_capture")
```### 开始会话```python
selected_channels = [c for c in [mic, display, system_audio] if c]
await client.start_capture_session(
    capture_session_id=session.id,
    channels=selected_channels,
    primary_video_channel_id=display.id if display else None,
)
```### 停止会话```python
await client.stop_capture()
await client.shutdown()
```---

## 频道

由`client.list_channels()`返回。按类型对可用设备进行分组。```python
channels = await client.list_channels()
for ch in channels.all():
    print(f"  {ch.id} ({ch.type}): {ch.name}")

mic = channels.mics.default
display = channels.displays.default
system_audio = channels.system_audio.default
```### 频道组

|物业 |类型 |描述 |
|----------|------|-------------|
| `channels.mics` | `频道组` |可用麦克风 |
| `频道.显示` | `频道组` |可用屏幕显示|
| `channels.system_audio` | `频道组` |可用的系统音频源|

### ChannelGroup 方法和属性

|会员|类型 |描述 |
|--------|------|-------------|
| `组.默认` | `频道` |组中的默认频道（或“无”） |
| `group.all()` | `列表[频道]` |群组内所有频道 |

### 通道属性

|物业 |类型 |描述 |
|----------|------|-------------|
| `ch.id` | `str` |唯一的频道ID |
| `ch.type` | `str` |通道类型（“麦克风”、“显示”、“系统音频”）|
| `ch.name` | `str` |人类可读的频道名称 |
| `ch.store` | `布尔` |是否保留录音（设置为“True”保存）|

如果没有“store = True”，流将被实时处理但不会保存。

---

## RTStreams 和 AI 管道

会话激活后，使用 session.get_rtstream() 检索 RTStream 对象。

有关 RTStream 方法（索引、转录、警报、批量配置），请参阅 [rtstream-reference.md](rtstream-reference.md)。

---

## 会话生命周期```
  create_capture_session()
          │
          v
  ┌───────────────┐
  │    created     │
  └───────┬───────┘
          │  client.start_capture_session()
          v
  ┌───────────────┐     WebSocket: capture_session.starting
  │   starting     │ ──> Capture channels connect
  └───────┬───────┘
          │
          v
  ┌───────────────┐     WebSocket: capture_session.active
  │    active      │ ──> Start AI pipelines
  └───────┬──────────────┐
          │              │
          │              v
          │      ┌───────────────┐     WebSocket: capture_session.failed
          │      │    failed      │ ──> Inspect error payload and retry setup
          │      └───────────────┘
          │      unrecoverable capture error
          │
          │  client.stop_capture()
          v
  ┌───────────────┐     WebSocket: capture_session.stopping
  │   stopping     │ ──> Finalize streams
  └───────┬───────┘
          │
          v
  ┌───────────────┐     WebSocket: capture_session.stopped
  │   stopped      │ ──> All streams finalized
  └───────┬───────┘
          │  (if store=True)
          v
  ┌───────────────┐     WebSocket: capture_session.exported
  │   exported     │ ──> Access video_id, stream_url, player_url
  └───────────────┘
```