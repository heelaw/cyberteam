# 时间线编辑指南

VideoDB 提供了一个非破坏性时间线编辑器，用于从多个资源编写视频、添加文本和图像叠加、混合音轨以及修剪剪辑 - 所有这些都在服务器端进行，无需重新编码或使用本地工具。使用它来修剪、组合剪辑、在视频上叠加音频/音乐、添加字幕以及分层文本或图像。

## 先决条件

视频、音频和图像**必须上传**到集合，然后才能用作时间线资产。对于字幕叠加，视频还必须**针对口语词建立索引**。

## 核心概念

### 时间轴

“时间轴”是一个虚拟合成层。资产可以**内联**（在主轨道上顺序排列）或作为**覆盖**（在特定时间戳分层）放置在其上。不会修改原始媒体；最终流是按需编译的。```python
from videodb.timeline import Timeline

timeline = Timeline(conn)
```### 资产

时间线上的每个元素都是**资产**。 VideoDB提供五种资产类型：

|资产|进口|主要用途 |
|--------|--------|-------------|
| `视频资产` | `从 videodb.asset 导入 VideoAsset` |视频剪辑（修剪、排序）|
| `音频资产` | `从 videodb.asset 导入 AudioAsset` |音乐、SFX、旁白 |
| `图像资产` | `从 videodb.asset 导入 ImageAsset` |徽标、缩略图、叠加层 |
| `文本资源` | `从 videodb.asset 导入 TextAsset、TextStyle` |标题、说明文字、下三分之一|
| `标题资产` | `从 videodb.editor 导入 CaptionAsset` |自动渲染字幕（编辑器 API）|

## 建立时间表

### 添加内嵌视频剪辑

内嵌资源在主视频轨道上依次播放。 `add_inline` 方法仅接受 `VideoAsset`：```python
from videodb.asset import VideoAsset

video_a = coll.get_video(video_id_a)
video_b = coll.get_video(video_id_b)

timeline = Timeline(conn)
timeline.add_inline(VideoAsset(asset_id=video_a.id))
timeline.add_inline(VideoAsset(asset_id=video_b.id))

stream_url = timeline.generate_stream()
```### 修剪/子剪辑

在“VideoAsset”上使用“start”和“end”来提取一部分：```python
# Take only seconds 10–30 from the source video
clip = VideoAsset(asset_id=video.id, start=10, end=30)
timeline.add_inline(clip)
```### 视频资源参数

|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `asset_id` | `str` |必填|视频媒体ID |
| `开始` | `浮动` | `0` |修剪开始（秒）|
| `结束` | `浮动\|无` | `无` |修剪结束（“无”=完整）|

> **警告：** SDK 不验证负时间戳。传递 `start=-5` 会被默默接受，但会产生损坏或意外的输出。在创建“VideoAsset”之前，始终确保“start >= 0”、“start < end”和“end <= video.length”。

## 文本叠加

在时间轴上的任意点添加标题、下三分之一或说明文字：```python
from videodb.asset import TextAsset, TextStyle

title = TextAsset(
    text="Welcome to the Demo",
    duration=5,
    style=TextStyle(
        fontsize=36,
        fontcolor="white",
        boxcolor="black",
        alpha=0.8,
        font="Sans",
    ),
)

# Overlay the title at the very start (t=0)
timeline.add_overlay(0, title)
```### 文本样式参数

|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `字体大小` | `int` | `24` |字体大小（以像素为单位）|
| `字体颜色` | `str` | `“黑色”` | CSS 颜色名称或十六进制 |
| `fontcolor_expr` | `str` | `""` |动态字体颜色表达|
| `阿尔法` | `浮动` | `1.0` |文本不透明度 (0.0–1.0) |
| `字体` | `str` | `“Sans”` |字体家族 |
| `盒子` | `布尔` | '真实' |启用背景框 |
| `盒子颜色` | `str` | `“白色”` |背景框颜色|
| `boxborderw` | `str` | `"10"` |框边框宽度 |
| `盒子` | `int` | `0` |框宽度覆盖 |
| `盒子` | `int` | `0` |盒子高度覆盖 |
| `行距` | `int` | `0` |行间距|
| `文本对齐` | `str` | `“T”` |框内的文本对齐 |
| `y_align` | `str` | `“文本”` |垂直对齐参考|
| `边框` | `int` | `0` |文本边框宽度 |
| `边框颜色` | `str` | `“黑色”` |文本边框颜色 |
| `扩展` | `str` | `“正常”` |文本扩展模式|
| `基准时间` | `int` | `0` |基于时间的表达式的基准时间 |
| `修复边界` | `布尔` | ‘假’|修复文本边界 |
| `文本塑造` | `布尔` | '真实' |启用文本整形 |
| `阴影颜色` | `str` | `“黑色”` |阴影颜色|
| `shadowx` | `int` | `0` |阴影 X 偏移 |
| '阴暗' | `int` | `0` |阴影 Y 偏移 |
| `制表符大小` | `int` | `4` |制表符大小（以空格为单位）|
| `x` | `str` | `"(main_w-text_w)/2"` |水平位置表达式 |
| `y` | `str` | `"(main_h-text_h)/2"` |垂直位置表达式 |

## 音频叠加

在视频轨道上分层背景音乐、音效或画外音：```python
from videodb.asset import AudioAsset

music = coll.get_audio(music_id)

audio_layer = AudioAsset(
    asset_id=music.id,
    disable_other_tracks=False,
    fade_in_duration=2,
    fade_out_duration=2,
)

# Start the music at t=0, overlaid on the video track
timeline.add_overlay(0, audio_layer)
```### 音频资源参数

|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `asset_id` | `str` |必填|音频媒体 ID |
| `开始` | `浮动` | `0` |修剪开始（秒）|
| `结束` | `浮动\|无` | `无` |修剪结束（“无”=完整）|
| `禁用其他轨道` | `布尔` | '真实' |当 True 时，使其他音轨静音 |
| `淡入持续时间` | `浮动` | `0` |淡入秒数（最多 5 秒）|
| `淡出持续时间` | `浮动` | `0` |淡出秒数（最多 5 秒）|

## 图像叠加

添加徽标、水印或生成的图像作为叠加层：```python
from videodb.asset import ImageAsset

logo = coll.get_image(logo_id)

logo_overlay = ImageAsset(
    asset_id=logo.id,
    duration=10,
    width=120,
    height=60,
    x=20,
    y=20,
)

timeline.add_overlay(0, logo_overlay)
```### 图像资源参数

|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `asset_id` | `str` |必填|图像媒体 ID |
| `宽度` | `int\|str` | `100` |显示宽度|
| `高度` | `int\|str` | `100` |显示高度|
| `x` | `int` | `80` |水平位置（距左侧 px）|
| `y` | `int` | `20` |垂直位置（距离顶部 px）|
| `持续时间` | `浮动\|无` | `无` |显示持续时间（秒）|

## 字幕叠加

有两种方法可以为视频添加字幕。

### 方法 1：字幕工作流程（最简单）

使用 video.add_subtitle() 将字幕直接刻录到视频流上。这在内部使用了`videodb.timeline.Timeline`：```python
from videodb import SubtitleStyle

# Video must have spoken words indexed first (force=True skips if already done)
video.index_spoken_words(force=True)

# Add subtitles with default styling
stream_url = video.add_subtitle()

# Or customise the subtitle style
stream_url = video.add_subtitle(style=SubtitleStyle(
    font_name="Arial",
    font_size=22,
    primary_colour="&H00FFFFFF",
    bold=True,
))
```### 方法 2：编辑器 API（高级）

编辑器 API (`videodb.editor`) 提供了一个基于轨道的合成系统，其中包含 `CaptionAsset`、`Clip`、`Track` 及其自己的 `Timeline`。这是与上面使用的“videodb.timeline.Timeline”不同的 API。```python
from videodb.editor import (
    CaptionAsset,
    Clip,
    Track,
    Timeline as EditorTimeline,
    FontStyling,
    BorderAndShadow,
    Positioning,
    CaptionAnimation,
)

# Video must have spoken words indexed first (force=True skips if already done)
video.index_spoken_words(force=True)

# Create a caption asset
caption = CaptionAsset(
    src="auto",
    font=FontStyling(name="Clear Sans", size=30),
    primary_color="&H00FFFFFF",
    back_color="&H00000000",
    border=BorderAndShadow(outline=1),
    position=Positioning(margin_v=30),
    animation=CaptionAnimation.box_highlight,
)

# Build an editor timeline with tracks and clips
editor_tl = EditorTimeline(conn)
track = Track()
track.add_clip(start=0, clip=Clip(asset=caption, duration=video.length))
editor_tl.add_track(track)
stream_url = editor_tl.generate_stream()
```### CaptionAsset 参数

|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `src` | `str` | `“自动”` |字幕源（`"auto"` 或 base64 ASS 字符串）|
| `字体` | `字体样式\|无` | `FontStyling()` |字体样式（名称、大小、粗体、斜体等）|
| `原色` | `str` | `"&H00FFFFFF"` |主要文本颜色（ASS 格式）|
| `次要颜色` | `str` | `"&H000000FF"` |辅助文本颜色（ASS 格式）|
| `背景颜色` | `str` | `"&H00000000"` |背景颜色（ASS 格式）|
| `边界` | `BorderAndShadow\|无` | `BorderAndShadow()` |边框和阴影样式|
| `位置` | `定位\|无` | `定位()` |标题对齐和边距 |
| `动画` | `CaptionAnimation\|无` | `无` |动画效果（例如，`box_highlight`、`reveal`、`karaoke`）|

## 编译和流式传输

组装时间线后，将其编译为可流式传输的 URL。流立即生成 - 没有渲染等待时间。```python
stream_url = timeline.generate_stream()
print(f"Stream: {stream_url}")
```有关更多流媒体选项（分段流、搜索流、音频播放），请参阅 [streaming.md](streaming.md)。

## 完整的工作流程示例

### 带标题卡的精彩片段```python
import videodb
from videodb import SearchType
from videodb.exceptions import InvalidRequestError
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# 1. Search for key moments
video.index_spoken_words(force=True)
try:
    results = video.search("product announcement", search_type=SearchType.semantic)
    shots = results.get_shots()
except InvalidRequestError as exc:
    if "No results found" in str(exc):
        shots = []
    else:
        raise

# 2. Build timeline
timeline = Timeline(conn)

# Title card
title = TextAsset(
    text="Product Launch Highlights",
    duration=4,
    style=TextStyle(fontsize=48, fontcolor="white", boxcolor="#1a1a2e", alpha=0.95),
)
timeline.add_overlay(0, title)

# Append each matching clip
for shot in shots:
    asset = VideoAsset(asset_id=shot.video_id, start=shot.start, end=shot.end)
    timeline.add_inline(asset)

# 3. Generate stream
stream_url = timeline.generate_stream()
print(f"Highlight reel: {stream_url}")
```### 徽标叠加背景音乐```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, AudioAsset, ImageAsset

conn = videodb.connect()
coll = conn.get_collection()

main_video = coll.get_video(main_video_id)
music = coll.get_audio(music_id)
logo = coll.get_image(logo_id)

timeline = Timeline(conn)

# Main video track
timeline.add_inline(VideoAsset(asset_id=main_video.id))

# Background music — disable_other_tracks=False to mix with video audio
timeline.add_overlay(
    0,
    AudioAsset(asset_id=music.id, disable_other_tracks=False, fade_in_duration=3),
)

# Logo in top-right corner for first 10 seconds
timeline.add_overlay(
    0,
    ImageAsset(asset_id=logo.id, duration=10, x=1140, y=20, width=120, height=60),
)

stream_url = timeline.generate_stream()
print(f"Final video: {stream_url}")
```### 多个视频的多剪辑蒙太奇```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

conn = videodb.connect()
coll = conn.get_collection()

clips = [
    {"video_id": "vid_001", "start": 5, "end": 15, "label": "Scene 1"},
    {"video_id": "vid_002", "start": 0, "end": 20, "label": "Scene 2"},
    {"video_id": "vid_003", "start": 30, "end": 45, "label": "Scene 3"},
]

timeline = Timeline(conn)
timeline_offset = 0.0

for clip in clips:
    # Add a label as an overlay on each clip
    label = TextAsset(
        text=clip["label"],
        duration=2,
        style=TextStyle(fontsize=32, fontcolor="white", boxcolor="#333333"),
    )
    timeline.add_inline(
        VideoAsset(asset_id=clip["video_id"], start=clip["start"], end=clip["end"])
    )
    timeline.add_overlay(timeline_offset, label)
    timeline_offset += clip["end"] - clip["start"]

stream_url = timeline.generate_stream()
print(f"Montage: {stream_url}")
```## 两个时间轴 API

VideoDB 有两个独立的时间线系统。它们**不可互换**：

| | `videodb.timeline.Timeline` | `videodb.editor.Timeline`（编辑器 API）|
|---|---|---|
| **导入** | `从 videodb.timeline 导入时间轴` | `from videodb.editor import Timeline as EditorTimeline` |
| **资产** | `VideoAsset`、`AudioAsset`、`ImageAsset`、`TextAsset` | `CaptionAsset`、`Clip`、`Track` |
| **方法** | `add_inline()`、`add_overlay()` | `add_track()` 与 `Track` / `Clip` |
| **最适合** |视频合成、叠加、多剪辑编辑 |带动画的标题/副标题样式 |

请勿将一个 API 中的资产混合到另一个 API 中。 `CaptionAsset` 仅适用于编辑器 API。 `VideoAsset` / `AudioAsset` / `ImageAsset` / `TextAsset` 仅适用于 `videodb.timeline.Timeline`。

## 限制和约束

时间线编辑器专为**非破坏性线性合成**而设计。 **不支持**以下操作：

### 不可能

|限制|详情 |
|---|---|
| **没有过渡或效果** |剪辑之间没有交叉淡入淡出、划像、溶解或过渡。所有剪辑都是硬剪辑。 |
| **没有视频对视频（画中画）** | `add_inline()` 只接受 `VideoAsset`。您不能将一个视频流叠加在另一个视频流之上。图像叠加可以近似静态画中画，但不能近似实时视频。 |
| **无速度或播放控制** |没有慢动作、快进、反向播放或时间重新映射。 `VideoAsset` 没有 `speed` 参数。 |
| **无裁剪、缩放或平移** |无法裁剪视频帧的区域、应用缩放效果或平移帧。 `video.reframe()` 仅用于宽高比转换。 |
| **没有视频滤镜或颜色分级** |没有亮度、对比度、饱和度、色调或色彩校正调整。 |
| **没有动画文字** | `TextAsset` 在其整个持续时间内都是静态的。没有淡入/淡出、移动或动画。对于动画字幕，请将“CaptionAsset”与编辑器 API 结合使用。 |
| **无混合文本样式** |单个“TextAsset”有一个“TextStyle”。不能在单个文本块中混合粗体、斜体或颜色。 |
| **没有空白或纯色剪辑** |无法创建纯色框架、黑屏或独立标题卡。文本和图像叠加需要在内联轨道上的下方有一个“VideoAsset”。 |
| **无音量控制** | `AudioAsset` 没有 `volume` 参数。音频可以是全音量，也可以通过“disable_other_tracks”静音。不能以降低的水平混合。 |
| **无关键帧动画** |无法随时间更改叠加属性（例如，将图像从位置 A 移动到 B）。 |

### 约束

|约束|详情 |
|---|---|
| **音频淡出最长 5 秒** | `fade_in_duration` 和 `fade_out_duration` 的上限均为 5 秒。 |
| **叠加定位是绝对的** |叠加使用从时间线开始算起的绝对时间戳。重新排列内联剪辑不会移动其叠加层。 |
| **内联轨道仅限视频** | `add_inline()` 只接受 `VideoAsset`。音频、图像和文本必须使用“add_overlay()”。 |
| **无覆盖到剪辑绑定** |叠加层放置在固定的时间轴时间戳处。无法将叠加层附加到特定的内嵌剪辑，使其随之移动。 |

## 提示

- **非破坏性**：时间线永远不会修改源媒体。您可以从相同的资源创建多个时间线。
- **叠加堆叠**：多个叠加可以在同一时间戳开始。音频叠加混合在一起；图像/文本按添加顺序覆盖图层。
- **内联仅限于 VideoAsset**：`add_inline()` 只接受 `VideoAsset`。对“AudioAsset”、“ImageAsset”和“TextAsset”使用“add_overlay()”。
- **修剪精度**：“VideoAsset”和“AudioAsset”上的“start”/“end”以秒为单位。
- **视频音频静音**：在“AudioAsset”上设置“disable_other_tracks=True”，可在叠加音乐或旁白时将原始视频音频静音。
- **淡入淡出限制**：“AudioAsset”上的“fade_in_duration”和“fade_out_duration”最长为 5 秒。
- **生成的媒体**：使用`coll.generate_music()`、`coll.generate_sound_effect()`、`coll.generate_voice()`和`coll.generate_image()`创建可立即用作时间轴资产的媒体。