#VideoDB技能

**视频、直播和桌面会话的感知+记忆+动作。**

## 何时使用

### 桌面感知
- 启动/停止**桌面会话**捕获**屏幕、麦克风和系统音频**
- 流式传输**实时上下文**并存储**情景会话内存**
- 针对所说内容和屏幕上发生的情况运行**实时警报/触发器**
- 生成**会议摘要**、可搜索的时间线和**可播放的证据链接**

### 视频摄取+流
- 摄取 **文件或 URL** 并返回 **可播放的网络流链接**
- 转码/标准化：**编解码器、比特率、fps、分辨率、宽高比**

### 索引+搜索（时间戳+证据）
- 构建**视觉**、**口语**和**关键字**索引
- 搜索并返回带有**时间戳**和**可播放证据**的确切时刻
- 从搜索结果自动创建**剪辑**

### 时间轴编辑+生成
- 字幕：**生成**、**翻译**、**烧录**
- 叠加：**文本/图像/品牌**、动态字幕
- 音频：**背景音乐**、**画外音**、**配音**
- 通过**时间线操作**进行编程组合和导出

### 直播（RTSP）+监控
- 连接**RTSP/实时直播**
- 运行**实时视觉和口头理解**并发出**事件/警报**以监控工作流程

## 它是如何工作的

### 常用输入
- 本地 **文件路径**、公共 **URL** 或 **RTSP URL**
- 桌面捕获请求：**开始/停止/总结会话**
- 所需的操作：获取理解上下文、转码规范、索引规范、搜索查询、剪辑范围、时间线编辑、警报规则

### 通用输出
- **流媒体网址**
- 带有**时间戳**和**证据链接**的搜索结果
- 生成的资产：字幕、音频、图像、剪辑
- **实时流的事件/警报有效负载**
- 桌面**会话摘要**和内存条目

### 运行Python代码

在运行任何 VideoDB 代码之前，更改到项目目录并加载环境变量：```python
from dotenv import load_dotenv
load_dotenv(".env")

import videodb
conn = videodb.connect()
```这将从以下位置读取“VIDEO_DB_API_KEY”：
1.环境（如果已经导出）
2.当前目录下项目的`.env`文件

如果密钥丢失，“videodb.connect()”会自动引发“AuthenticationError”。

当短内联命令起作用时，请勿编写脚本文件。

编写内联 Python（`python -c "..."`）时，请始终使用格式正确的代码 - 使用分号分隔语句并保持可读性。对于任何超过 3 个语句的内容，请改用定界文档：```bash
python << 'EOF'
from dotenv import load_dotenv
load_dotenv(".env")

import videodb
conn = videodb.connect()
coll = conn.get_collection()
print(f"Videos: {len(coll.get_videos())}")
EOF
```### 设置

当用户要求“设置 videodb”或类似内容时：

### 1.安装SDK```bash
pip install "videodb[capture]" python-dotenv
```如果 `videodb[capture]` 在 Linux 上失败，请安装而不安装额外的捕获：```bash
pip install videodb python-dotenv
```### 2.配置API密钥

用户必须使用**任一**方法设置“VIDEO_DB_API_KEY”：

- **在终端中导出**（在启动 Claude 之前）：`export VIDEO_DB_API_KEY=your-key`
- **项目 `.env` 文件**：将 `VIDEO_DB_API_KEY=your-key` 保存在项目的 `.env` 文件中

在 [console.videodb.io](https://console.videodb.io) 获取免费的 API 密钥（50 个免费上传，无需信用卡）。

**请勿**自行读取、写入或处理 API 密钥。始终让用户设置它。

### 快速参考

### 上传媒体```python
# URL
video = coll.upload(url="https://example.com/video.mp4")

# YouTube
video = coll.upload(url="https://www.youtube.com/watch?v=VIDEO_ID")

# Local file
video = coll.upload(file_path="/path/to/video.mp4")
```### 文字记录 + 副标题```python
# force=True skips the error if the video is already indexed
video.index_spoken_words(force=True)
text = video.get_transcript_text()
stream_url = video.add_subtitle()
```### 搜索内部视频```python
from videodb.exceptions import InvalidRequestError

video.index_spoken_words(force=True)

# search() raises InvalidRequestError when no results are found.
# Always wrap in try/except and treat "No results found" as empty.
try:
    results = video.search("product demo")
    shots = results.get_shots()
    stream_url = results.compile()
except InvalidRequestError as e:
    if "No results found" in str(e):
        shots = []
    else:
        raise
```###场景搜索```python
import re
from videodb import SearchType, IndexType, SceneExtractionType
from videodb.exceptions import InvalidRequestError

# index_scenes() has no force parameter — it raises an error if a scene
# index already exists. Extract the existing index ID from the error.
try:
    scene_index_id = video.index_scenes(
        extraction_type=SceneExtractionType.shot_based,
        prompt="Describe the visual content in this scene.",
    )
except Exception as e:
    match = re.search(r"id\s+([a-f0-9]+)", str(e))
    if match:
        scene_index_id = match.group(1)
    else:
        raise

# Use score_threshold to filter low-relevance noise (recommended: 0.3+)
try:
    results = video.search(
        query="person writing on a whiteboard",
        search_type=SearchType.semantic,
        index_type=IndexType.scene,
        scene_index_id=scene_index_id,
        score_threshold=0.3,
    )
    shots = results.get_shots()
    stream_url = results.compile()
except InvalidRequestError as e:
    if "No results found" in str(e):
        shots = []
    else:
        raise
```### 时间轴编辑

**重要：** 在构建时间线之前始终验证时间戳：
- `start` 必须 >= 0（负值被默默接受，但会产生损坏的输出）
- `start` 必须 < `end`
- `end` 必须 <= `video.length````python
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

timeline = Timeline(conn)
timeline.add_inline(VideoAsset(asset_id=video.id, start=10, end=30))
timeline.add_overlay(0, TextAsset(text="The End", duration=3, style=TextStyle(fontsize=36)))
stream_url = timeline.generate_stream()
```### 视频转码（分辨率/质量变化）```python
from videodb import TranscodeMode, VideoConfig, AudioConfig

# Change resolution, quality, or aspect ratio server-side
job_id = conn.transcode(
    source="https://example.com/video.mp4",
    callback_url="https://example.com/webhook",
    mode=TranscodeMode.economy,
    video_config=VideoConfig(resolution=720, quality=23, aspect_ratio="16:9"),
    audio_config=AudioConfig(mute=False),
)
```### 重构宽高比（针对社交平台）

**警告：** `reframe()` 是一个缓慢的服务器端操作。对于长视频可能需要
几分钟，可能会超时。最佳实践：
- 尽可能使用“start”/“end”限制短片段
- 对于完整长度的视频，使用“callback_url”进行异步处理
- 首先在“时间轴”上修剪视频，然后重新构建较短的结果```python
from videodb import ReframeMode

# Always prefer reframing a short segment:
reframed = video.reframe(start=0, end=60, target="vertical", mode=ReframeMode.smart)

# Async reframe for full-length videos (returns None, result via webhook):
video.reframe(target="vertical", callback_url="https://example.com/webhook")

# Presets: "vertical" (9:16), "square" (1:1), "landscape" (16:9)
reframed = video.reframe(start=0, end=60, target="square")

# Custom dimensions
reframed = video.reframe(start=0, end=60, target={"width": 1280, "height": 720})
```### 生成媒体```python
image = coll.generate_image(
    prompt="a sunset over mountains",
    aspect_ratio="16:9",
)
```## 错误处理```python
from videodb.exceptions import AuthenticationError, InvalidRequestError

try:
    conn = videodb.connect()
except AuthenticationError:
    print("Check your VIDEO_DB_API_KEY")

try:
    video = coll.upload(url="https://example.com/video.mp4")
except InvalidRequestError as e:
    print(f"Upload failed: {e}")
```### 常见陷阱

|场景|错误信息 |解决方案 |
|----------|--------------|----------|
|为已索引的视频建立索引 | `视频的口语索引已存在` |如果已编入索引，请使用“video.index_spoken_words(force=True)”跳过 |
|场景索引已存在 | `ID 为 XXXX 的场景索引已存在` |使用 `re.search(r"id\s+([a-f0-9]+)", str(e))` 从错误中提取现有的 `scene_index_id` |
|搜索未找到匹配项 | `InvalidRequestError：未找到结果` |捕获异常并视为空结果 (`shots = []`) |
|重构超时 |无限期阻止长视频 |使用 `start`/`end` 来限制段，或通过 `callback_url` 进行异步 |
|时间轴上的负时间戳 |悄然产生断流|在创建“VideoAsset”之前始终验证“start >= 0” |
| `generate_video()` / `create_collection()` 失败 | `不允许操作`或`最大限制` |计划门控功能 — 告知用户计划限制 |

## 示例

### 规范提示
- “启动桌面捕获并在出现密码字段时发出警报。”
- “记录我的会话并在结束时生成可操作的摘要。”
- “提取此文件并返回可播放的流链接。”
- “索引此文件夹并查找每个有人物的场景，返回时间戳。”
- “生成字幕、刻录字幕并添加轻快的背景音乐。”
- “连接此 RTSP URL 并在有人进入该区域时发出警报。”

### 屏幕录制（桌面捕获）

使用“ws_listener.py”在录制会话期间捕获 WebSocket 事件。桌面捕获仅支持 **macOS**。

#### 快速入门

1. **选择状态目录**： `STATE_DIR="${VIDEODB_EVENTS_DIR:-$HOME/.local/state/videodb}"`
2. **启动监听器**: `VIDEODB_EVENTS_DIR="$STATE_DIR" python script/ws_listener.py --clear "$STATE_DIR" &`
3. **获取 WebSocket ID**: `cat "$STATE_DIR/videodb_ws_id"`
4. **运行捕获代码**（完整工作流程请参阅reference/capture.md）
5. **事件写入**：`$STATE_DIR/videodb_events.jsonl`

每当您开始新的捕获运行时，请使用“--clear”，这样过时的脚本和视觉事件就不会泄漏到新会话中。

#### 查询事件```python
import json
import os
import time
from pathlib import Path

events_dir = Path(os.environ.get("VIDEODB_EVENTS_DIR", Path.home() / ".local" / "state" / "videodb"))
events_file = events_dir / "videodb_events.jsonl"
events = []

if events_file.exists():
    with events_file.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

transcripts = [e["data"]["text"] for e in events if e.get("channel") == "transcript"]
cutoff = time.time() - 300
recent_visual = [
    e for e in events
    if e.get("channel") == "visual_index" and e["unix_ts"] > cutoff
]
```## 附加文档

参考文档位于与 SKILL.md 文件相邻的“reference/”目录中。如果需要，请使用 Glob 工具找到它。

- [reference/api-reference.md](reference/api-reference.md) - 完整的 VideoDB Python SDK API 参考
- [reference/search.md](reference/search.md) - 视频搜索深入指南（基于口语和场景）
- [reference/editor.md](reference/editor.md) - 时间轴编辑、资源和合成
- [reference/streaming.md](reference/streaming.md) - HLS 流媒体和即时播放
- [reference/generative.md](reference/generative.md) - AI 驱动的媒体生成（图像、视频、音频）
- [reference/rtstream.md](reference/rtstream.md) - 直播流摄取工作流程 (RTSP/RTMP)
- [reference/rtstream-reference.md](reference/rtstream-reference.md) - RTStream SDK方法和AI管道
- [reference/capture.md](reference/capture.md) - 桌面捕获工作流程
- [reference/capture-reference.md](reference/capture-reference.md) - 捕获 SDK 和 WebSocket 事件
- [reference/use-cases.md](reference/use-cases.md) - 常见视频处理模式和示例

**当 VideoDB 支持该操作时，请勿使用 ffmpeg、moviepy 或本地编码工具**。以下内容均由 VideoDB 在服务器端处理：修剪、组合剪辑、叠加音频或音乐、添加字幕、文本/图像叠加、转码、分辨率更改、宽高比转换、根据平台要求调整大小、转录和媒体生成。仅回退到本地工具来执行参考/editor.md 中的限制下列出的操作（过渡、速度更改、裁剪/缩放、颜色分级、体积混合）。

### 何时使用什么

|问题 | VideoDB解决方案|
|------|------------------|
|平台拒绝视频宽高比或分辨率 | `video.reframe()` 或 `conn.transcode()` 与 `VideoConfig` |
|需要调整 Twitter/Instagram/TikTok 的视频大小 | `video.reframe(target="vertical")` 或 `target="square"` |
|需要更改分辨率（例如 1080p → 720p）| `conn.transcode()` 和 `VideoConfig(分辨率=720)` |
|需要在视频上叠加音频/音乐| “时间轴”上的“音频资产” |
|需要添加字幕 | `video.add_subtitle()` 或 `CaptionAsset` |
|需要组合/修剪剪​​辑 | “时间轴”上的“VideoAsset” |
|需要生成画外音、音乐或 SFX | `coll.generate_voice()`、`generate_music()`、`generate_sound_effect()` |

## 出处

该技能的参考资料在本地“skills/videodb/reference/”下提供。
使用上面的本地副本，而不是在运行时跟踪外部存储库链接。

**维护者：** [VideoDB](https://www.videodb.io/)