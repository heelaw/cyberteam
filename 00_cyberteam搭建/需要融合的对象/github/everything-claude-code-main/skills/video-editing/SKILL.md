# 视频编辑

人工智能辅助编辑真实镜头。不是根据提示生成。快速编辑现有视频。

## 何时激活

- 用户想要编辑、剪切或构建视频片段
- 将长录音变成短格式内容
- 从原始捕获中构建视频博客、教程或演示视频
- 向现有视频添加叠加、字幕、音乐或画外音
- 为不同平台（YouTube、TikTok、Instagram）重新构建视频
- 用户说“编辑视频”、“剪切此片段”、“制作视频博客”或“视频工作流程”

## 核心论文

当您不再要求 AI 视频编辑创建整个视频并开始使用它来压缩、构建和增强真实素材时，AI 视频编辑会非常有用。价值不在于世代。该值是压缩。

## 管道```
Screen Studio / raw footage
  → Claude / Codex
  → FFmpeg
  → Remotion
  → ElevenLabs / fal.ai
  → Descript or CapCut
```每一层都有特定的工作。不要跳层。不要试图让一种工具做所有事情。

## 第 1 层：捕捉（Screen Studio / 原始素材）

收集源材料：
- **Screen Studio**：用于应用程序演示、编码会话、浏览器工作流程的精美屏幕录制
- **原始摄像机镜头**：视频博客镜头、采访、活动录音
- **通过 VideoDB 进行桌面捕获**：具有实时上下文的会话记录（请参阅“videodb”技能）

输出：准备组织的原始文件。

## 第 2 层：组织（Claude / Codex）

使用克劳德代码或 Codex 可以：
- **转录和标签**：生成转录，识别主题和主题
- **计划结构**：决定保留什么，削减什么，什么顺序有效
- **识别死区**：查找停顿、切线、重复镜头
- **生成编辑决策列表**：剪切的时间戳、要保留的片段
- **Scaffold FFmpeg 和 Remotion 代码**：生成命令和组合```
Example prompt:
"Here's the transcript of a 4-hour recording. Identify the 8 strongest segments
for a 24-minute vlog. Give me FFmpeg cut commands for each segment."
```这一层是关于结构，而不是最终的创意品味。

## 第 3 层：确定性剪切 (FFmpeg)

FFmpeg 处理无聊但关键的工作：分割、修剪、连接和预处理。

### 按时间戳提取段```bash
ffmpeg -i raw.mp4 -ss 00:12:30 -to 00:15:45 -c copy segment_01.mp4
```### 从编辑决策列表中批量剪切```bash
#!/bin/bash
# cuts.txt: start,end,label
while IFS=, read -r start end label; do
  ffmpeg -i raw.mp4 -ss "$start" -to "$end" -c copy "segments/${label}.mp4"
done < cuts.txt
```### 连接段```bash
# Create file list
for f in segments/*.mp4; do echo "file '$f'"; done > concat.txt
ffmpeg -f concat -safe 0 -i concat.txt -c copy assembled.mp4
```### 创建代理以加快编辑速度```bash
ffmpeg -i raw.mp4 -vf "scale=960:-2" -c:v libx264 -preset ultrafast -crf 28 proxy.mp4
```### 提取音频进行转录```bash
ffmpeg -i raw.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav
```### 标准化音频电平```bash
ffmpeg -i segment.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:v copy normalized.mp4
```## 第 4 层：可编程组合（远程）

远程将编辑问题转化为可组合代码。使用它来处理传统编辑器感到痛苦的事情：

### 何时使用远程

- 叠加：文本、图像、品牌、下三分之一
- 数据可视化：图表、统计数据、动画数字
- 动态图形：过渡、解释动画
- 可组合场景：跨视频可重复使用的模板
- 产品演示：带注释的屏幕截图、UI 亮点

### 基本 Remotion 组成```tsx
import { AbsoluteFill, Sequence, Video, useCurrentFrame } from "remotion";

export const VlogComposition: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill>
      {/* Main footage */}
      <Sequence from={0} durationInFrames={300}>
        <Video src="/segments/intro.mp4" />
      </Sequence>

      {/* Title overlay */}
      <Sequence from={30} durationInFrames={90}>
        <AbsoluteFill style={{
          justifyContent: "center",
          alignItems: "center",
        }}>
          <h1 style={{
            fontSize: 72,
            color: "white",
            textShadow: "2px 2px 8px rgba(0,0,0,0.8)",
          }}>
            The AI Editing Stack
          </h1>
        </AbsoluteFill>
      </Sequence>

      {/* Next segment */}
      <Sequence from={300} durationInFrames={450}>
        <Video src="/segments/demo.mp4" />
      </Sequence>
    </AbsoluteFill>
  );
};
```### 渲染输出```bash
npx remotion render src/index.ts VlogComposition output.mp4
```有关详细模式和 API 参考，请参阅 [Remotion 文档](https://www.remotion.dev/docs)。

## 第 5 层：生成资产 (ElevenLabs / fal.ai)

仅生成您需要的内容。不要生成整个视频。

### ElevenLabs 的配音```python
import os
import requests

resp = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
    headers={
        "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
        "Content-Type": "application/json"
    },
    json={
        "text": "Your narration text here",
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
)
with open("voiceover.mp3", "wb") as f:
    f.write(resp.content)
```### 音乐和 SFX 与 fal.ai

使用“fal-ai-media”技能：
- 背景音乐生成
- 音效（视频转音频的ThinkSound模型）
- 过渡声音

### 使用 fal.ai 生成视觉效果

用于插入不存在的镜头、缩略图或幕后花絮：```
generate(app_id: "fal-ai/nano-banana-pro", input_data: {
  "prompt": "professional thumbnail for tech vlog, dark background, code on screen",
  "image_size": "landscape_16_9"
})
```### VideoDB 生成音频

如果配置了VideoDB：```python
voiceover = coll.generate_voice(text="Narration here", voice="alloy")
music = coll.generate_music(prompt="lo-fi background for coding vlog", duration=120)
sfx = coll.generate_sound_effect(prompt="subtle whoosh transition")
```## 第 6 层：最终抛光（描述/CapCut）

最后一层是人类。使用传统编辑器可以：
- **节奏**：调整感觉太快或太慢的剪辑
- **字幕**：自动生成，然后手动清理
- **颜色分级**：基本校正和情绪
- **最终音频混合**：平衡语音、音乐和 SFX 级别
- **导出**：特定于平台的格式和质量设置

这就是品味的所在。 AI消除了重复性工作。你做最后的决定。

## 社交媒体重构

不同的平台需要不同的宽高比：

|平台|纵横比 |分辨率|
|----------|-------------|------------|
| YouTube | 16:9 | 16:9 1920x1080 | 1920x1080
| TikTok / 卷轴 | 9:16 | 1080x1920 | 1080x1920
| Instagram 动态 | 1:1 | 1080x1080 | 1080x1080
| X / 推特 | 16:9 或 1:1 | 1280x720 或 720x720 |

### 使用 FFmpeg 重构```bash
# 16:9 to 9:16 (center crop)
ffmpeg -i input.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" vertical.mp4

# 16:9 to 1:1 (center crop)
ffmpeg -i input.mp4 -vf "crop=ih:ih,scale=1080:1080" square.mp4
```### 使用 VideoDB 重构```python
from videodb import ReframeMode

# Smart reframe (AI-guided subject tracking)
reframed = video.reframe(start=0, end=60, target="vertical", mode=ReframeMode.smart)
```## 场景检测和自动剪切

### FFmpeg场景检测```bash
# Detect scene changes (threshold 0.3 = moderate sensitivity)
ffmpeg -i input.mp4 -vf "select='gt(scene,0.3)',showinfo" -vsync vfr -f null - 2>&1 | grep showinfo
```### 自动剪切的静音检测```bash
# Find silent segments (useful for cutting dead air)
ffmpeg -i input.mp4 -af silencedetect=noise=-30dB:d=2 -f null - 2>&1 | grep silence
```### 高亮提取

使用Claude来分析脚本+场景时间戳：```
"Given this transcript with timestamps and these scene change points,
identify the 5 most engaging 30-second clips for social media."
```## 每个工具最擅长什么

|工具|实力|弱点|
|------|----------|----------|
|克劳德/法典|组织、规划、代码生成 |不是创意品味层|
| FFmpeg |确定性剪切、批处理、格式转换 |没有可视化编辑 UI |
|远程|可编程叠加、可组合场景、可重用模板 |非开发人员的学习曲线 |
|屏幕工作室|立即美化屏幕录制|仅屏幕截图|
|十一实验室 |声音、旁白、音乐、SFX |不是工作流程的中心 |
|描述/CapCut |最终节奏、字幕、润色 |手动，不可自动化 |

## 关键原则

1. **编辑，而不是生成。** 此工作流程用于剪切真实素材，而不是根据提示进行创建。
2. **结构优先于风格。** 在接触任何视觉效果之前，先在第 2 层将故事讲好。
3. **FFmpeg 是支柱。** 无聊但至关重要。长镜头变得易于管理。
4. **Remotion 以实现可重复性。** 如果您要多次执行此操作，请将其设为 Remotion 组件。
5. **选择性生成。** 仅对不存在的资产使用人工智能生成，而不是对所有资产使用人工智能生成。
6. **品味是最后一层。** AI消除重复性工作。您做出最后的创意决定。

## 相关技能

- `fal-ai-media` — AI 图像、视频和音频生成
- `videodb` — 服务器端视频处理、索引和流媒体
- `content-engine` — 平台原生内容分发