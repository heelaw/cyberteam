# 流媒体和播放

VideoDB 按需生成流，返回可在任何标准视频播放器中立即播放的 HLS 兼容 URL。无渲染时间或导出等待 - 编辑、搜索和合成立即流式传输。

## 先决条件

在生成流之前，视频**必须上传**到集合。对于基于搜索的流，视频还必须被**索引**（口语和/或场景）。有关索引详细信息，请参阅 [search.md](search.md)。

## 核心概念

### 流生成

VideoDB 中的每个视频、搜索结果和时间线都可以生成**流 URL**。此 URL 指向按需编译的 HLS（HTTP Live Streaming）清单。```python
# From a video
stream_url = video.generate_stream()

# From a timeline
stream_url = timeline.generate_stream()

# From search results
stream_url = results.compile()
```## 流式传输单个视频

### 基本播放```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# Generate stream URL
stream_url = video.generate_stream()
print(f"Stream: {stream_url}")

# Open in default browser
video.play()
```### 带字幕```python
# Index and add subtitles first
video.index_spoken_words(force=True)
stream_url = video.add_subtitle()

# Returned URL already includes subtitles
print(f"Subtitled stream: {stream_url}")
```### 具体细分

通过传递时间戳范围的时间线仅流式传输视频的一部分：```python
# Stream seconds 10-30 and 60-90
stream_url = video.generate_stream(timeline=[(10, 30), (60, 90)])
print(f"Segment stream: {stream_url}")
```## 流式传输时间线作品

构建多资产组合并实时传输：```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, AudioAsset, ImageAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()

video = coll.get_video(video_id)
music = coll.get_audio(music_id)

timeline = Timeline(conn)

# Main video content
timeline.add_inline(VideoAsset(asset_id=video.id))

# Background music overlay (starts at second 0)
timeline.add_overlay(0, AudioAsset(asset_id=music.id))

# Text overlay at the beginning
timeline.add_overlay(0, TextAsset(
    text="Live Demo",
    duration=3,
    style=TextStyle(fontsize=48, fontcolor="white", boxcolor="#000000"),
))

# Generate the composed stream
stream_url = timeline.generate_stream()
print(f"Composed stream: {stream_url}")
```**重要提示：** `add_inline()` 仅接受 `VideoAsset`。对“AudioAsset”、“ImageAsset”和“TextAsset”使用“add_overlay()”。

详细的时间线编辑请参见[editor.md](editor.md)。

## 流式传输搜索结果

将搜索结果编译到所有匹配段的单个流中：```python
from videodb import SearchType
from videodb.exceptions import InvalidRequestError

video.index_spoken_words(force=True)
try:
    results = video.search("key announcement", search_type=SearchType.semantic)

    # Compile all matching shots into one stream
    stream_url = results.compile()
    print(f"Search results stream: {stream_url}")

    # Or play directly
    results.play()
except InvalidRequestError as exc:
    if "No results found" in str(exc):
        print("No matching announcement segments were found.")
    else:
        raise
```### 流式传输个人搜索结果```python
from videodb.exceptions import InvalidRequestError

try:
    results = video.search("product demo", search_type=SearchType.semantic)
    for i, shot in enumerate(results.get_shots()):
        stream_url = shot.generate_stream()
        print(f"Hit {i+1} [{shot.start:.1f}s-{shot.end:.1f}s]: {stream_url}")
except InvalidRequestError as exc:
    if "No results found" in str(exc):
        print("No product demo segments matched the query.")
    else:
        raise
```## 音频播放

获取音频内容的签名播放 URL：```python
audio = coll.get_audio(audio_id)
playback_url = audio.generate_url()
print(f"Audio URL: {playback_url}")
```## 完整的工作流程示例

### 搜索到流管道

将搜索、时间线合成和流式传输合并到一个工作流程中：```python
import videodb
from videodb import SearchType
from videodb.exceptions import InvalidRequestError
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

video.index_spoken_words(force=True)

# Search for key moments
queries = ["introduction", "main demo", "Q&A"]
timeline = Timeline(conn)
timeline_offset = 0.0

for query in queries:
    try:
        results = video.search(query, search_type=SearchType.semantic)
        shots = results.get_shots()
    except InvalidRequestError as exc:
        if "No results found" in str(exc):
            shots = []
        else:
            raise

    if not shots:
        continue

    # Add the section label where this batch starts in the compiled timeline
    timeline.add_overlay(timeline_offset, TextAsset(
        text=query.title(),
        duration=2,
        style=TextStyle(fontsize=36, fontcolor="white", boxcolor="#222222"),
    ))

    for shot in shots:
        timeline.add_inline(
            VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
        )
        timeline_offset += shot.end - shot.start

stream_url = timeline.generate_stream()
print(f"Dynamic compilation: {stream_url}")
```### 多视频流

将不同视频的剪辑合并到一个流中：```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset

conn = videodb.connect()
coll = conn.get_collection()

video_clips = [
    {"id": "vid_001", "start": 0, "end": 15},
    {"id": "vid_002", "start": 10, "end": 30},
    {"id": "vid_003", "start": 5, "end": 25},
]

timeline = Timeline(conn)
for clip in video_clips:
    timeline.add_inline(
        VideoAsset(asset_id=clip["id"], start=clip["start"], end=clip["end"])
    )

stream_url = timeline.generate_stream()
print(f"Multi-video stream: {stream_url}")
```### 条件流汇编

根据搜索可用性动态构建流：```python
import videodb
from videodb import SearchType
from videodb.exceptions import InvalidRequestError
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

video.index_spoken_words(force=True)

timeline = Timeline(conn)

# Try to find specific content; fall back to full video
topics = ["opening remarks", "technical deep dive", "closing"]

found_any = False
timeline_offset = 0.0
for topic in topics:
    try:
        results = video.search(topic, search_type=SearchType.semantic)
        shots = results.get_shots()
    except InvalidRequestError as exc:
        if "No results found" in str(exc):
            shots = []
        else:
            raise

    if shots:
        found_any = True
        timeline.add_overlay(timeline_offset, TextAsset(
            text=topic.title(),
            duration=2,
            style=TextStyle(fontsize=32, fontcolor="white", boxcolor="#1a1a2e"),
        ))
        for shot in shots:
            timeline.add_inline(
                VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
            )
            timeline_offset += shot.end - shot.start

if found_any:
    stream_url = timeline.generate_stream()
    print(f"Curated stream: {stream_url}")
else:
    # Fall back to full video stream
    stream_url = video.generate_stream()
    print(f"Full video stream: {stream_url}")
```### 现场活动回顾

将事件记录处理为具有多个部分的可流式回顾：```python
import videodb
from videodb import SearchType
from videodb.exceptions import InvalidRequestError
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, AudioAsset, ImageAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()

# Upload event recording
event = coll.upload(url="https://example.com/event-recording.mp4")
event.index_spoken_words(force=True)

# Generate background music
music = coll.generate_music(
    prompt="upbeat corporate background music",
    duration=120,
)

# Generate title image
title_img = coll.generate_image(
    prompt="modern event recap title card, dark background, professional",
    aspect_ratio="16:9",
)

# Build the recap timeline
timeline = Timeline(conn)
timeline_offset = 0.0

# Main video segments from search
try:
    keynote = event.search("keynote announcement", search_type=SearchType.semantic)
    keynote_shots = keynote.get_shots()[:5]
except InvalidRequestError as exc:
    if "No results found" in str(exc):
        keynote_shots = []
    else:
        raise
if keynote_shots:
    keynote_start = timeline_offset
    for shot in keynote_shots:
        timeline.add_inline(
            VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
        )
        timeline_offset += shot.end - shot.start
else:
    keynote_start = None

try:
    demo = event.search("product demo", search_type=SearchType.semantic)
    demo_shots = demo.get_shots()[:5]
except InvalidRequestError as exc:
    if "No results found" in str(exc):
        demo_shots = []
    else:
        raise
if demo_shots:
    demo_start = timeline_offset
    for shot in demo_shots:
        timeline.add_inline(
            VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
        )
        timeline_offset += shot.end - shot.start
else:
    demo_start = None

# Overlay title card image
timeline.add_overlay(0, ImageAsset(
    asset_id=title_img.id, width=100, height=100, x=80, y=20, duration=5
))

# Overlay section labels at the correct timeline offsets
if keynote_start is not None:
    timeline.add_overlay(max(5, keynote_start), TextAsset(
        text="Keynote Highlights",
        duration=3,
        style=TextStyle(fontsize=40, fontcolor="white", boxcolor="#0d1117"),
    ))
if demo_start is not None:
    timeline.add_overlay(max(5, demo_start), TextAsset(
        text="Demo Highlights",
        duration=3,
        style=TextStyle(fontsize=36, fontcolor="white", boxcolor="#0d1117"),
    ))

# Overlay background music
timeline.add_overlay(0, AudioAsset(
    asset_id=music.id, fade_in_duration=3
))

# Stream the final recap
stream_url = timeline.generate_stream()
print(f"Event recap: {stream_url}")
```---

## 提示

- **HLS 兼容性**：流 URL 返回 HLS 清单 (`.m3u8`)。它们原生在 Safari 中工作，并通过 hls.js 或类似库在其他浏览器中工作。
- **按需编译**：当请求时，流在服务器端编译。第一次播放可能会有短暂的编译延迟；相同作品的后续播放将被缓存。
- **缓存**：在不带参数的情况下第二次调用 `video.generate_stream()` 将返回缓存的流 URL，而不是重新编译。
- **分段流**：`video.generate_stream(timeline=[(start, end)])` 是在不构建完整的 `Timeline` 对象的情况下流式传输特定剪辑的最快方法。
- **内联与覆盖**：`add_inline()`仅接受`VideoAsset`并将资源按顺序放置在主轨道上。 `add_overlay()` 接受 `AudioAsset`、`ImageAsset` 和 `TextAsset` 并在给定的开始时间将它们分层。
- **TextStyle 默认值**：`TextStyle` 默认为 `font='Sans'`、`fontcolor='black'`。使用“boxcolor”（而不是“bgcolor”）作为文本的背景颜色。
- **与生成结合**：使用`coll.generate_music(prompt,uration)`和`coll.generate_image(prompt,aspect_ratio)`为时间线合成创建资产。
- **播放**：`.play()` 在默认系统浏览器中打开流 URL。对于编程使用，请直接使用 URL 字符串。