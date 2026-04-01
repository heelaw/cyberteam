# fal.ai 媒体生成

通过 MCP 使用 fal.ai 模型生成图像、视频和音频。

## 何时激活

- 用户想要根据文本提示生成图像
- 从文本或图像创建视频
- 生成语音、音乐或声音效果
- 任何媒体生成任务
- 用户说“生成图像”、“创建视频”、“文本转语音”、“制作缩略图”或类似内容

## MCP 要求

必须配置 fal.ai MCP 服务器。添加到`~/.claude.json`：```json
"fal-ai": {
  "command": "npx",
  "args": ["-y", "fal-ai-mcp-server"],
  "env": { "FAL_KEY": "YOUR_FAL_KEY_HERE" }
}
```在 [fal.ai](https://fal.ai) 获取 API 密钥。

## MCP 工具

fal.ai MCP 提供以下工具：
- `search` — 按关键字查找可用型号
- `find` — 获取模型详细信息和参数
- `generate` — 使用参数运行模型
- `result` — 检查异步生成状态
- `status` — 检查作业状态
- `cancel` — 取消正在运行的作业
- `estimate_cost` — 估计发电成本
- `models` — 列出流行模型
- `upload` — 上传文件用作输入

---

## 图像生成

### 纳米香蕉 2（快速）
最适合：快速迭代、草稿、文本到图像、图像编辑。```
generate(
  model_name: "fal-ai/nano-banana-2",
  input: {
    "prompt": "a futuristic cityscape at sunset, cyberpunk style",
    "image_size": "landscape_16_9",
    "num_images": 1,
    "seed": 42
  }
)
```### Nano Banana Pro (High Fidelity)
Best for: production images, realism, typography, detailed prompts.```
generate(
  model_name: "fal-ai/nano-banana-pro",
  input: {
    "prompt": "professional product photo of wireless headphones on marble surface, studio lighting",
    "image_size": "square",
    "num_images": 1,
    "guidance_scale": 7.5
  }
)
```### 常用图像参数

|参数 |类型 |选项|笔记|
|--------|------|---------|--------|
| `提示` |字符串|必填|描述你想要什么 |
| `图像大小` |字符串| `正方形`、`portrait_4_3`、`landscape_16_9`、`portrait_16_9`、`landscape_4_3` |纵横比|
| `num_images` |数量 | 1-4 | 1-4生成多少 |
| `种子` |数量 |任意整数 |再现性|
| `guidance_scale` |数量 | 1-20 | 1-20遵循提示的程度（更高=更字面意思） |

### 图像编辑
将 Nano Banana 2 与输入图像一起使用以进行修复、修复或风格转换：```
# First upload the source image
upload(file_path: "/path/to/image.png")

# Then generate with image input
generate(
  model_name: "fal-ai/nano-banana-2",
  input: {
    "prompt": "same scene but in watercolor style",
    "image_url": "<uploaded_url>",
    "image_size": "landscape_16_9"
  }
)
```---

## 视频生成

### Seedance 1.0 Pro（字节跳动）
最适合：具有高运动质量的文本到视频、图像到视频。```
generate(
  model_name: "fal-ai/seedance-1-0-pro",
  input: {
    "prompt": "a drone flyover of a mountain lake at golden hour, cinematic",
    "duration": "5s",
    "aspect_ratio": "16:9",
    "seed": 42
  }
)
```### Kling Video v3 Pro
最适合：带有本地音频生成的文本/图像到视频。```
generate(
  model_name: "fal-ai/kling-video/v3/pro",
  input: {
    "prompt": "ocean waves crashing on a rocky coast, dramatic clouds",
    "duration": "5s",
    "aspect_ratio": "16:9"
  }
)
```### Veo 3（谷歌 DeepMind）
最适合：带声音的视频、高视觉质量。```
generate(
  model_name: "fal-ai/veo-3",
  input: {
    "prompt": "a bustling Tokyo street market at night, neon signs, crowd noise",
    "aspect_ratio": "16:9"
  }
)
```### 图像到视频
从现有图像开始：```
generate(
  model_name: "fal-ai/seedance-1-0-pro",
  input: {
    "prompt": "camera slowly zooms out, gentle wind moves the trees",
    "image_url": "<uploaded_image_url>",
    "duration": "5s"
  }
)
```### 视频参数

|参数 |类型 |选项|笔记|
|--------|------|---------|--------|
| `提示` |字符串|必填|描述视频 |
| `持续时间` |字符串| `"5s"`, `"10s"` |视频长度|
| `纵横比` |字符串| `"16:9"`、`"9:16"`、`"1:1"` |帧率|
| `种子` |数量 |任意整数 |再现性|
| `image_url` |字符串|网址 |图像转视频的源图像 |

---

## 音频生成

### CSM-1B（会话语音）
文本转语音，具有自然的会话质量。```
generate(
  model_name: "fal-ai/csm-1b",
  input: {
    "text": "Hello, welcome to the demo. Let me show you how this works.",
    "speaker_id": 0
  }
)
```### ThinkSound（视频转音频）
从视频内容生成匹配的音频。```
generate(
  model_name: "fal-ai/thinksound",
  input: {
    "video_url": "<video_url>",
    "prompt": "ambient forest sounds with birds chirping"
  }
)
```### ElevenLabs（通过 API，无 MCP）
对于专业的语音合成，直接使用ElevenLabs：```python
import os
import requests

resp = requests.post(
    "https://api.elevenlabs.io/v1/text-to-speech/<voice_id>",
    headers={
        "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
        "Content-Type": "application/json"
    },
    json={
        "text": "Your text here",
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
)
with open("output.mp3", "wb") as f:
    f.write(resp.content)
```### VideoDB 生成音频
如果配置了 VideoDB，则使用其生成音频：```python
# Voice generation
audio = coll.generate_voice(text="Your narration here", voice="alloy")

# Music generation
music = coll.generate_music(prompt="upbeat electronic background music", duration=30)

# Sound effects
sfx = coll.generate_sound_effect(prompt="thunder crack followed by rain")
```---

## 成本估算

在生成之前，检查预计成本：```
estimate_cost(model_name: "fal-ai/nano-banana-pro", input: {...})
```## 模型发现

查找特定任务的模型：```
search(query: "text to video")
find(model_name: "fal-ai/seedance-1-0-pro")
models()
```## 提示

- 在迭代提示时使用“seed”以获得可重现的结果
- 从成本较低的型号（Nano Banana 2）开始进行快速迭代，然后切换到 Pro 进行最终版本
- 对于视频，保持提示具有描述性但简洁——重点关注动作和场景
- 图像到视频比纯文本到视频产生更受控制的结果
- 在运行昂贵的视频生成之前检查“estimate_cost”

## 相关技能

- `videodb` — 视频处理、编辑和流媒体
- “视频编辑”——人工智能驱动的视频编辑工作流程
- `content-engine` — 社交平台的内容创建