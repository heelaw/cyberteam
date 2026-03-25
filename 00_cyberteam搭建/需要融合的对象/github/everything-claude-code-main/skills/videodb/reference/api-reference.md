# 完整的 API 参考

VideoDB 技能的参考资料。有关使用指南和工作流程选择，请从 [../SKILL.md](../SKILL.md) 开始。

＃＃ 联系```python
import videodb

conn = videodb.connect(
    api_key="your-api-key",      # or set VIDEO_DB_API_KEY env var
    base_url=None,                # custom API endpoint (optional)
)
```**返回：** `Connection` 对象

### 连接方法

|方法|返回|描述 |
|--------|---------|-------------|
| `conn.get_collection(collection_id="default")` | `集合` |获取集合（如果没有 ID，则默认）|
| `conn.get_collections()` | `列表[集合]` |列出所有集合 |
| `conn.create_collection(名称、描述、is_public=False)` | `集合` |创建新集合 |
| `conn.update_collection(id, 名称, 描述)` | `集合` |更新收藏 |
| `conn.check_usage()` | `字典` |获取帐户使用统计信息 |
| `conn.upload(源、媒体类型、名称、...)` | `视频\|音频\|图像` |上传至默认收藏|
| `conn.record_meeting(meeting_url, bot_name, ...)` | `会议` |录制会议 |
| `conn.create_capture_session(...)` | `捕获会话` |创建捕获会话（请参阅 [capture-reference.md](capture-reference.md)）|
| `conn.youtube_search(查询、result_threshold、持续时间)` | `列表[字典]` |搜索 YouTube |
| `conn.transcode(源、callback_url、模式、...)` | `str` |转码视频（返回作业 ID）|
| `conn.get_transcode_details(job_id)` | `字典` |获取转码作业状态和详细信息 |
| `conn.connect_websocket(collection_id)` | `WebSocketConnection` |连接到 WebSocket（请参阅 [capture-reference.md](capture-reference.md)）|

### 转码

使用自定义分辨率、质量和音频设置对来自 URL 的视频进行转码。处理发生在服务器端——不需要本地 ffmpeg。```python
from videodb import TranscodeMode, VideoConfig, AudioConfig

job_id = conn.transcode(
    source="https://example.com/video.mp4",
    callback_url="https://example.com/webhook",
    mode=TranscodeMode.economy,
    video_config=VideoConfig(resolution=720, quality=23),
    audio_config=AudioConfig(mute=False),
)
```#### 转码参数

|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `来源` | `str` |必填|要转码的视频的 URL（最好是可下载的 URL）|
| `callback_url` | `str` |必填|转码完成时接收回调的URL |
| `模式` | `转码模式` | `TranscodeMode.economy` |转码速度：“经济”或“闪电”|
| `视频配置` | `视频配置` | `VideoConfig()` |视频编码设置|
| `音频配置` | `音频配置` | `AudioConfig()` |音频编码设置|

返回作业 ID (`str`)。使用 conn.get_transcode_details(job_id) 检查作业状态。```python
details = conn.get_transcode_details(job_id)
```#### 视频配置```python
from videodb import VideoConfig, ResizeMode

config = VideoConfig(
    resolution=720,              # Target resolution height (e.g. 480, 720, 1080)
    quality=23,                  # Encoding quality (lower = better, default 23)
    framerate=30,                # Target framerate
    aspect_ratio="16:9",         # Target aspect ratio
    resize_mode=ResizeMode.crop, # How to fit: crop, fit, or pad
)
```|领域|类型 |默认 |描述 |
|--------|------|---------|-------------|
| `决议` | `int\|无` | `无` |目标分辨率高度（以像素为单位）|
| `质量` | `int` | `23` |编码质量（较低=较高质量）|
| `帧率` | `int\|无` | `无` |目标帧率|
| `纵横比` | `str\|无` | `无` |目标宽高比（例如“16:9”、“9:16”）|
| `调整大小模式` | `str` | `ResizeMode.crop` |调整大小策略：“crop”、“fit”或“pad” |

#### 音频配置```python
from videodb import AudioConfig

config = AudioConfig(mute=False)
```|领域|类型 |默认 |描述 |
|--------|------|---------|-------------|
| `静音` | `布尔` | ‘假’|将音轨静音 |

## 收藏```python
coll = conn.get_collection()
```### 收集方法

|方法|返回|描述 |
|--------|---------|-------------|
| `coll.get_videos()` | `列表[视频]` |列出所有视频 |
| `coll.get_video(video_id)` | `视频` |获取具体视频 |
| `coll.get_audios()` | `列表[音频]` |列出所有音频 |
| `coll.get_audio(audio_id)` | `音频` |获取特定音频 |
| `coll.get_images()` | `列表[图像]` |列出所有图像 |
| `coll.get_image(image_id)` | `图像` |获取具体图像 |
| `coll.upload(url=None, file_path=None, media_type=None, name=None)` | `视频\|音频\|图像` |上传媒体 |
| `coll.search（查询，search_type，index_type，score_threshold，命名空间，scene_index_id，...）` | `搜索结果` |跨集合搜索（仅语义；关键字和场景搜索引发“NotImplementedError”）|
| `coll.generate_image(提示，aspect_ratio="1:1")` | `图像` |利用 AI 生成图像 |
| `coll.generate_video（提示，持续时间=5）` | `视频` |使用 AI 生成视频 |
| `coll.generate_music(提示，持续时间=5)` | `音频` |使用 AI 生成音乐 |
| `coll.generate_sound_effect（提示，持续时间=2）` | `音频` |生成音效 |
| `coll.generate_voice(text, voice_name="默认")` | `音频` |从文本生成语音 |
| `coll.generate_text（提示，model_name =“基本”，response_type =“文本”）` | `字典` | LLM 文本生成 — 通过 `["output"]` 访问结果 |
| `coll.dub_video(video_id, language_code)` | `视频` |将视频配音成另一种语言 |
| `coll.record_meeting(meeting_url, bot_name, ...)` | `会议` |录制现场会议 |
| `coll.create_capture_session(...)` | `捕获会话` |创建捕获会话（请参阅 [capture-reference.md](capture-reference.md)）|
| `coll.get_capture_session(...)` | `捕获会话` |检索捕获会话（请参阅 [capture-reference.md](capture-reference.md)）|
| `coll.connect_rtstream(url, 名称, ...)` | `RTStream` |连接到直播流（请参阅 [rtstream-reference.md](rtstream-reference.md)）|
| `coll.make_public()` | `无` |公开收藏|
| `coll.make_private()` | `无` |将收藏设为私有 |
| `coll.delete_video(video_id)` | `无` |删除视频 |
| `coll.delete_audio(audio_id)` | `无` |删除音频 |
| `coll.delete_image(image_id)` | `无` |删除图像 |
| `coll.delete()` | `无` |删除集合 |

### 上传参数```python
video = coll.upload(
    url=None,            # Remote URL (HTTP, YouTube)
    file_path=None,      # Local file path
    media_type=None,     # "video", "audio", or "image" (auto-detected if omitted)
    name=None,           # Custom name for the media
    description=None,    # Description
    callback_url=None,   # Webhook URL for async notification
)
```## 视频对象```python
video = coll.get_video(video_id)
```### 视频属性

|物业 |类型 |描述 |
|----------|------|-------------|
| `视频.id` | `str` |唯一视频ID |
| `video.collection_id` | `str` |父集合 ID |
| `视频名称` | `str` |视频名称 |
| `视频.描述` | `str` |视频说明|
| `视频长度` | `浮动` |持续时间（秒）|
| `video.stream_url` | `str` |默认流 URL |
| `video.player_url` | `str` |播放器嵌入 URL |
| `video.thumbnail_url` | `str` |缩略图网址 |

### 视频方法

|方法|返回|描述 |
|--------|---------|-------------|
| `video.generate_stream（时间线=无）` | `str` |生成流 URL（`[(start, end)]` 元组的可选时间线）|
| `video.play()` | `str` |在浏览器中打开流，返回播放器 URL |
| `video.index_spoken_words（language_code=None，force=False）` | `无` |用于搜索的索引语音。如果已经索引，请使用“force=True”跳过。 |
| `video.index_scenes(extraction_type、prompt、extraction_config、metadata、model_name、name、scenes、callback_url)` | `str` |索引视觉场景（返回 scene_index_id）|
| `video.index_visuals（提示，batch_config，...）` | `str` |索引视觉效果（返回 scene_index_id）|
| `video.index_audio（提示，模型名称，...）` | `str` |使用 LLM 索引音频（返回 scene_index_id）|
| `video.get_transcript(开始=无，结束=无)` | `列表[字典]` |获取带时间戳的文字记录 |
| `video.get_transcript_text(start=None, end=None)` | `str` |获取完整的成绩单文本 |
| `video.generate_transcript(force=None)` | `字典` |生成成绩单 |
| `video.translate_transcript（语言，additional_notes）` | `列表[字典]` |翻译成绩单|
| `video.search（查询，search_type，index_type，过滤器，**kwargs）` | `搜索结果` |在视频中搜索 |
| `video.add_subtitle(style=SubtitleStyle())` | `str` |添加字幕（返回流 URL）|
| `video.generate_thumbnail(时间=无)` | `str\|图像` |生成缩略图 |
| `video.get_thumbnails()` | `列表[图像]` |获取所有缩略图 |
| `video.extract_scenes（extraction_type，extraction_config）` | `场景集合` |提取场景|
| `video.reframe(开始、结束、目标、模式、callback_url)` | `视频\|无` |重新调整视频宽高比 |
| `video.clip(提示、内容类型、模型名称)` | `str` |根据提示生成剪辑（返回流 URL）|
| `video.insert_video（视频，时间戳）` | `str` |在时间戳处插入视频 |
| `video.download(name=None)` | `字典` |下载视频 |
| `视频.delete()` | `无` |删除视频 |

### 重构

通过可选的智能对象跟踪将视频转换为不同的宽高比。处理是在服务器端进行的。

> **警告：** Reframe 是一种缓慢的服务器端操作。长视频可能需要几分钟的时间，并且可能会超时。始终使用 `start`/`end` 来限制段，或传递 `callback_url` 进行异步处理。```python
from videodb import ReframeMode

# Always prefer short segments to avoid timeouts:
reframed = video.reframe(start=0, end=60, target="vertical", mode=ReframeMode.smart)

# Async reframe for full-length videos (returns None, result via webhook):
video.reframe(target="vertical", callback_url="https://example.com/webhook")

# Custom dimensions
reframed = video.reframe(start=0, end=60, target={"width": 1080, "height": 1080})
```#### 重构参数

|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `开始` | `浮动\|无` | `无` |开始时间（以秒为单位）（无 = 开始）|
| `结束` | `浮动\|无` | `无` |结束时间（以秒为单位）（无 = 视频结束）|
| `目标` | `str\|dict` | `“垂直”` |预设字符串 (`"vertical"`、`"square"`、`"landscape"`) 或 `{"width": int, "height": int}` |
| `模式` | `str` | `ReframeMode.smart` | “简单”（中心裁剪）或“智能”（对象跟踪）|
| `callback_url` | `str\|无` | `无` |异步通知的 Webhook URL |

当没有提供 `callback_url` 时，返回一个 `Video` 对象，否则返回 `None`。

## 音频对象```python
audio = coll.get_audio(audio_id)
```### 音频属性

|物业 |类型 |描述 |
|----------|------|-------------|
| `音频.id` | `str` |唯一的音频ID |
| `audio.collection_id` | `str` |父集合 ID |
| `音频.name` | `str` |音频名称 |
| `音频长度` | `浮动` |持续时间（秒）|

### 音频方法

|方法|返回|描述 |
|--------|---------|-------------|
| `audio.generate_url()` | `str` |生成用于播放的签名 URL |
| `audio.get_transcript(开始=无，结束=无)` | `列表[字典]` |获取带时间戳的文字记录 |
| `audio.get_transcript_text(开始=无，结束=无)` | `str` |获取完整的成绩单文本 |
| `audio.generate_transcript(force=None)` | `字典` |生成成绩单 |
| `audio.delete()` | `无` |删除音频 |

## 图像对象```python
image = coll.get_image(image_id)
```### 图像属性

|物业 |类型 |描述 |
|----------|------|-------------|
| `图像.id` | `str` |唯一的图像ID |
| `image.collection_id` | `str` |父集合 ID |
| `图像.名称` | `str` |图片名称|
| `图像.url` | `str\|无` |图像 URL（对于生成的图像可能是“无”——使用“generate_url()”代替）|

### 图像方法

|方法|返回|描述 |
|--------|---------|-------------|
| `image.generate_url()` | `str` |生成签名 URL |
| `image.delete()` | `无` |删除图像 |

## 时间轴和编辑器

### 时间轴```python
from videodb.timeline import Timeline

timeline = Timeline(conn)
```|方法|返回|描述 |
|--------|---------|-------------|
| `timeline.add_inline(asset)` | `无` |在主轨道上依次添加“VideoAsset” |
| `timeline.add_overlay(start, asset)` | `无` |在时间戳处叠加“AudioAsset”、“ImageAsset”或“TextAsset” |
| `timeline.generate_stream()` | `str` |编译并获取流 URL |

### 资产类型

#### 视频资源```python
from videodb.asset import VideoAsset

asset = VideoAsset(
    asset_id=video.id,
    start=0,              # trim start (seconds)
    end=None,             # trim end (seconds, None = full)
)
```#### 音频资源```python
from videodb.asset import AudioAsset

asset = AudioAsset(
    asset_id=audio.id,
    start=0,
    end=None,
    disable_other_tracks=True,   # mute original audio when True
    fade_in_duration=0,          # seconds (max 5)
    fade_out_duration=0,         # seconds (max 5)
)
```#### 图像资源```python
from videodb.asset import ImageAsset

asset = ImageAsset(
    asset_id=image.id,
    duration=None,        # display duration (seconds)
    width=100,            # display width
    height=100,           # display height
    x=80,                 # horizontal position (px from left)
    y=20,                 # vertical position (px from top)
)
```#### 文本资源```python
from videodb.asset import TextAsset, TextStyle

asset = TextAsset(
    text="Hello World",
    duration=5,
    style=TextStyle(
        fontsize=24,
        fontcolor="black",
        boxcolor="white",       # background box colour
        alpha=1.0,
        font="Sans",
        text_align="T",         # text alignment within box
    ),
)
```#### CaptionAsset（编辑器 API）

CaptionAsset属于Editor API，它有自己的Timeline、Track和Clip系统：```python
from videodb.editor import CaptionAsset, FontStyling

asset = CaptionAsset(
    src="auto",                    # "auto" or base64 ASS string
    font=FontStyling(name="Clear Sans", size=30),
    primary_color="&H00FFFFFF",
)
```请参阅 [editor.md](editor.md#caption-overlays) 了解 CaptionAsset 与编辑器 API 的完整用法。

## 视频搜索参数```python
results = video.search(
    query="your query",
    search_type=SearchType.semantic,       # semantic, keyword, or scene
    index_type=IndexType.spoken_word,      # spoken_word or scene
    result_threshold=None,                 # max number of results
    score_threshold=None,                  # minimum relevance score
    dynamic_score_percentage=None,         # percentage of dynamic score
    scene_index_id=None,                   # target a specific scene index (pass via **kwargs)
    filter=[],                             # metadata filters for scene search
)
```> **注意：** `filter` 是 `video.search()` 中的显式命名参数。 `scene_index_id` 通过 `**kwargs` 传递到 API。
>
> **重要提示：** 当没有匹配项时，`video.search()` 会引发 `InvalidRequestError` 并显示消息“未找到结果”。始终将搜索调用包装在 try/ except 中。对于场景搜索，请使用 `score_threshold=0.3` 或更高值来过滤低相关性噪声。

对于场景搜索，请使用“search_type=SearchType.semantic”和“index_type=IndexType.scene”。当定位特定场景索引时传递 `scene_index_id`。详细信息请参见[search.md](search.md)。

## 搜索结果对象```python
results = video.search("query", search_type=SearchType.semantic)
```|方法|返回|描述 |
|--------|---------|-------------|
| `results.get_shots()` | `列表[镜头]` |获取匹配段的列表 |
| `结果.compile()` | `str` |将所有镜头编译成流 URL |
| `结果.play()` | `str` |在浏览器中打开编译流 |

### 射击属性

|物业 |类型 |描述 |
|----------|------|-------------|
| `shot.video_id` | `str` |源视频ID |
| `镜头.视频长度` | `浮动` |源视频时长|
| `镜头.视频标题` | `str` |来源视频标题|
| `射击.开始` | `浮动` |开始时间（秒）|
| `射击.结束` | `浮动` |结束时间（秒）|
| `镜头.文本` | `str` |匹配的文字内容 |
| `shot.search_score` | `浮动` |搜索相关性得分 |

|方法|返回|描述 |
|--------|---------|-------------|
| `shot.generate_stream()` | `str` |直播这个特定的镜头 |
| `shot.play()` | `str` |在浏览器中打开镜头流 |

## 会议对象```python
meeting = coll.record_meeting(
    meeting_url="https://meet.google.com/...",
    bot_name="Bot",
    callback_url=None,          # Webhook URL for status updates
    callback_data=None,         # Optional dict passed through to callbacks
    time_zone="UTC",            # Time zone for the meeting
)
```### 会议属性

|物业 |类型 |描述 |
|----------|------|-------------|
| `会议.id` | `str` |唯一的会议ID |
| `会议.collection_id` | `str` |父集合 ID |
| `会议状态` | `str` |现状 |
| `会议.video_id` | `str` |录制视频ID（完成后）|
| `会议.bot_name` | `str` |机器人名称 |
| `会议.会议标题` | `str` |会议标题 |
| `meeting.meeting_url` | `str` |会议网址 |
| `meeting.speaker_timeline` | `字典` |演讲者时间线数据|
| `会议.is_active` | `布尔` |如果正在初始化或处理则为 True |
| `会议已完成` | `布尔` |如果完成则为真 |

### 会议方法

|方法|返回|描述 |
|--------|---------|-------------|
| `会议.refresh()` | `会议` |从服务器刷新数据 |
| `meeting.wait_for_status（target_status，超时=14400，间隔=120）` | `布尔` |轮询直至状态达到|

## RTStream 和捕获

对于 RTStream（实时提取、索引、转录），请参阅 [rtstream-reference.md](rtstream-reference.md)。

对于捕获会话（桌面录制、CaptureClient、通道），请参阅 [capture-reference.md](capture-reference.md)。

## 枚举和常量

### 搜索类型```python
from videodb import SearchType

SearchType.semantic    # Natural language semantic search
SearchType.keyword     # Exact keyword matching
SearchType.scene       # Visual scene search (may require paid plan)
SearchType.llm         # LLM-powered search
```### 场景提取类型```python
from videodb import SceneExtractionType

SceneExtractionType.shot_based   # Automatic shot boundary detection
SceneExtractionType.time_based   # Fixed time interval extraction
SceneExtractionType.transcript   # Transcript-based scene extraction
```### 字幕样式```python
from videodb import SubtitleStyle

style = SubtitleStyle(
    font_name="Arial",
    font_size=18,
    primary_colour="&H00FFFFFF",
    bold=False,
    # ... see SubtitleStyle for all options
)
video.add_subtitle(style=style)
```### 副标题对齐方式和副标题边框样式```python
from videodb import SubtitleAlignment, SubtitleBorderStyle
```### 文本样式```python
from videodb import TextStyle
# or: from videodb.asset import TextStyle

style = TextStyle(
    fontsize=24,
    fontcolor="black",
    boxcolor="white",
    font="Sans",
    text_align="T",
    alpha=1.0,
)
```### 其他常量```python
from videodb import (
    IndexType,          # spoken_word, scene
    MediaType,          # video, audio, image
    Segmenter,          # word, sentence, time
    SegmentationType,   # sentence, llm
    TranscodeMode,      # economy, lightning
    ResizeMode,         # crop, fit, pad
    ReframeMode,        # simple, smart
    RTStreamChannelType,
)
```## 例外情况```python
from videodb.exceptions import (
    AuthenticationError,     # Invalid or missing API key
    InvalidRequestError,     # Bad parameters or malformed request
    RequestTimeoutError,     # Request timed out
    SearchError,             # Search operation failure (e.g. not indexed)
    VideodbError,            # Base exception for all VideoDB errors
)
```|例外 |共同原因|
|------------|-------------|
| `身份验证错误` | `VIDEO_DB_API_KEY` 缺失或无效 |
| `无效请求错误` |无效的 URL、不受支持的格式、错误的参数 |
| `请求超时错误` |服务器响应时间过长 |
| `搜索错误` |索引前搜索，搜索类型无效 |
| `VideodbError` |服务器错误、网络问题、一般故障 |