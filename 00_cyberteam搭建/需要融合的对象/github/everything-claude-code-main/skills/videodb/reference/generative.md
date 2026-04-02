# 生成媒体指南

VideoDB 提供由人工智能驱动的图像、视频、音乐、音效、语音和文本内容的生成。所有生成方法都在 **Collection** 对象上。

## 先决条件

在调用任何生成方法之前，您需要一个连接和一个集合引用：```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()
```## 图像生成

根据文本提示生成图像：```python
image = coll.generate_image(
    prompt="a futuristic cityscape at sunset with flying cars",
    aspect_ratio="16:9",
)

# Access the generated image
print(image.id)
print(image.generate_url())  # returns a signed download URL
```###generate_image参数

|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `提示` | `str` |必填|要生成的图像的文本描述 |
| `纵横比` | `str` | `"1:1"` |宽高比：“1:1”、“9:16”、“16:9”、“4:3”或“3:4”|
| `callback_url` | `str\|无` | `无` |接收异步回调的 URL |

返回带有“.id”、“.name”和“.collection_id”的“Image”对象。对于生成的图像，“.url”属性可能是“None”——始终使用“image.generate_url()”来获取可靠的签名下载 URL。

> **注意：** 与“Video”对象（使用“.generate_stream()”）不同，“Image”对象使用“.generate_url()”来检索图像 URL。仅针对某些图像类型（例如缩略图）填充“.url”属性。

## 视频生成

根据文本提示生成短视频剪辑：```python
video = coll.generate_video(
    prompt="a timelapse of a flower blooming in a garden",
    duration=5,
)

stream_url = video.generate_stream()
video.play()
```###generate_video参数

|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `提示` | `str` |必填|要生成的视频的文字描述 |
| `持续时间` | `int` | `5` |持续时间（以秒为单位）（必须是整数值，5-8）|
| `callback_url` | `str\|无` | `无` |接收异步回调的 URL |

返回一个“视频”对象。生成的视频会自动添加到集合中，并且可以像任何上传的视频一样用于时间轴、搜索和编辑。

## 音频生成

VideoDB 为不同的音频类型提供了三种单独的方法。

### 音乐

从文本描述生成背景音乐：```python
music = coll.generate_music(
    prompt="upbeat electronic music with a driving beat, suitable for a tech demo",
    duration=30,
)

print(music.id)
```|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `提示` | `str` |必填|音乐的文字描述 |
| `持续时间` | `int` | `5` |持续时间（秒）|
| `callback_url` | `str\|无` | `无` |接收异步回调的 URL |

### 音效

生成特定的音效：```python
sfx = coll.generate_sound_effect(
    prompt="thunderstorm with heavy rain and distant thunder",
    duration=10,
)
```|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `提示` | `str` |必填|音效文字描述|
| `持续时间` | `int` | `2` |持续时间（秒）|
| `配置` | `字典` | `{}` |附加配置|
| `callback_url` | `str\|无` | `无` |接收异步回调的 URL |

### 语音（文本转语音）

从文本生成语音：```python
voice = coll.generate_voice(
    text="Welcome to our product demo. Today we'll walk through the key features.",
    voice_name="Default",
)
```|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `文本` | `str` |必填|文本转换为语音 |
| `语音名称` | `str` | `“默认”` |语音使用|
| `配置` | `字典` | `{}` |附加配置|
| `callback_url` | `str\|无` | `无` |接收异步回调的 URL |

所有三个音频方法都会返回一个带有“.id”、“.name”、“.length”和“.collection_id”的“Audio”对象。

## 文本生成（LLM 集成）

使用 coll.generate_text() 运行 LLM 分析。这是一个**集合级**方法——直接在提示字符串中传递任何上下文（脚本、描述）。```python
# Get transcript from a video first
transcript_text = video.get_transcript_text()

# Generate analysis using collection LLM
result = coll.generate_text(
    prompt=f"Summarize the key points discussed in this video:\n{transcript_text}",
    model_name="pro",
)

print(result["output"])
```###generate_text 参数

|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `提示` | `str` |必填|提示 LLM 的背景 |
| `型号名称` | `str` | `“基本”` |型号层：“基本”、“专业”或“超级”|
| `响应类型` | `str` | `“文本”` |响应格式：`"text"` 或 `"json"` |

返回带有“output”键的“dict”。当 `response_type="text"` 时，`output` 是一个 `str`。当 `response_type="json"` 时，`output` 是一个 `dict`。```python
result = coll.generate_text(prompt="Summarize this", model_name="pro")
print(result["output"])  # access the actual text/dict
```### 使用 LLM 分析场景

将场景提取与文本生成结合起来：```python
from videodb import SceneExtractionType

# First index scenes
scenes = video.index_scenes(
    extraction_type=SceneExtractionType.time_based,
    extraction_config={"time": 10},
    prompt="Describe the visual content in this scene.",
)

# Get transcript for spoken context
transcript_text = video.get_transcript_text()
scene_descriptions = []
for scene in scenes:
    if isinstance(scene, dict):
        description = scene.get("description") or scene.get("summary")
    else:
        description = getattr(scene, "description", None) or getattr(scene, "summary", None)
    scene_descriptions.append(description or str(scene))

scenes_text = "\n".join(scene_descriptions)

# Analyze with collection LLM
result = coll.generate_text(
    prompt=(
        f"Given this video transcript:\n{transcript_text}\n\n"
        f"And these visual scene descriptions:\n{scenes_text}\n\n"
        "Based on the spoken and visual content, describe the main topics covered."
    ),
    model_name="pro",
)
print(result["output"])
```## 配音与翻译

### 配音视频

使用 collection 方法将视频配音成另一种语言：```python
dubbed_video = coll.dub_video(
    video_id=video.id,
    language_code="es",  # Spanish
)

dubbed_video.play()
```### dub_video 参数

|参数|类型 |默认 |描述 |
|------------|------|---------|------------|
| `video_id` | `str` |必填|要配音的视频 ID |
| `语言代码` | `str` |必填|目标语言代码（例如“es”、“fr”、“de”）|
| `callback_url` | `str\|无` | `无` |接收异步回调的 URL |

返回带有配音内容的“Video”对象。

### 翻译成绩单

翻译视频的文字记录而不配音：```python
translated = video.translate_transcript(
    language="Spanish",
    additional_notes="Use formal tone",
)

for entry in translated:
    print(entry)
```**支持的语言**包括：`en`、`es`、`fr`、`de`、`it`、`pt`、`ja`、`ko`、`zh`、`hi`、`ar` 等。

## 完整的工作流程示例

### 为视频生成旁白```python
import videodb

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# Get transcript
transcript_text = video.get_transcript_text()

# Generate narration script using collection LLM
result = coll.generate_text(
    prompt=(
        f"Write a professional narration script for this video content:\n"
        f"{transcript_text[:2000]}"
    ),
    model_name="pro",
)
script = result["output"]

# Convert script to speech
narration = coll.generate_voice(text=script)
print(f"Narration audio: {narration.id}")
```### 根据提示生成缩略图```python
thumbnail = coll.generate_image(
    prompt="professional video thumbnail showing data analytics dashboard, modern design",
    aspect_ratio="16:9",
)
print(f"Thumbnail URL: {thumbnail.generate_url()}")
```### 将生成的音乐添加到视频中```python
import videodb
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, AudioAsset

conn = videodb.connect()
coll = conn.get_collection()
video = coll.get_video("your-video-id")

# Generate background music
music = coll.generate_music(
    prompt="calm ambient background music for a tutorial video",
    duration=60,
)

# Build timeline with video + music overlay
timeline = Timeline(conn)
timeline.add_inline(VideoAsset(asset_id=video.id))
timeline.add_overlay(0, AudioAsset(asset_id=music.id, disable_other_tracks=False))

stream_url = timeline.generate_stream()
print(f"Video with music: {stream_url}")
```### 结构化 JSON 输出```python
transcript_text = video.get_transcript_text()

result = coll.generate_text(
    prompt=(
        f"Given this transcript:\n{transcript_text}\n\n"
        "Return a JSON object with keys: summary, topics (array), action_items (array)."
    ),
    model_name="pro",
    response_type="json",
)

# result["output"] is a dict when response_type="json"
print(result["output"]["summary"])
print(result["output"]["topics"])
```## 提示

- **生成的媒体是持久的**：所有生成的内容都存储在您的收藏中并且可以重复使用。
- **三种音频方法**：使用 `generate_music()` 制作背景音乐，使用 `generate_sound_effect()` 制作 SFX，使用 `generate_voice()` 制作文本转语音。没有统一的“generate_audio()”方法。
- **文本生成是集合级别的**：`coll.generate_text()`无法自动访问视频内容。使用 video.get_transcript_text() 获取脚本并将其传递到提示中。
- **模型等级**：“基本”是最快的，“专业”是平衡的，“超级”是最高质量。对于大多数分析任务，请使用“pro”。
- **组合生成类型**：生成用于叠加的图像、用于背景的音乐和用于旁白的语音，然后使用时间线进行创作（请参阅 [editor.md](editor.md)）。
- **提示质量很重要**：描述性的、具体的提示可以在所有生成类型中产生更好的结果。
- **图像的宽高比**：从“1:1”、“9:16”、“16:9”、“4:3”或“3:4”中选择。