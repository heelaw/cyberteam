# 样式预设参考

为“前端幻灯片”精心策划的视觉样式。

使用此文件用于：
- 强制视口适配 CSS 基础
- 预设选择和情绪映射
- CSS 陷阱和验证规则

仅抽象形状。除非用户明确要求，否则避免使用插图。

## 视口适配是没有商量余地的

每张幻灯片都必须完全适合一个视口。

### 黄金法则```text
Each slide = exactly one viewport height.
Too much content = split into more slides.
Never scroll inside a slide.
```### 密度限制

|幻灯片类型 |最大内容 |
|------------|-----------------|
|标题幻灯片| 1 个标题 + 1 个副标题 + 可选标语 |
|内容幻灯片| 1 个标题 + 4-6 个项目符号或 2 个段落 |
|特征网格|最多 6 张卡 |
|代码幻灯片|最多 8-10 行 |
|报价幻灯片| 1 条引用 + 归属 |
|图片幻灯片| 1 张图像，最好低于 60vh |

## 强制基础 CSS

将此块复制到每个生成的演示文稿中，然后将主题复制到其顶部。```css
/* ===========================================
   VIEWPORT FITTING: MANDATORY BASE STYLES
   =========================================== */

html, body {
    height: 100%;
    overflow-x: hidden;
}

html {
    scroll-snap-type: y mandatory;
    scroll-behavior: smooth;
}

.slide {
    width: 100vw;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    scroll-snap-align: start;
    display: flex;
    flex-direction: column;
    position: relative;
}

.slide-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    max-height: 100%;
    overflow: hidden;
    padding: var(--slide-padding);
}

:root {
    --title-size: clamp(1.5rem, 5vw, 4rem);
    --h2-size: clamp(1.25rem, 3.5vw, 2.5rem);
    --h3-size: clamp(1rem, 2.5vw, 1.75rem);
    --body-size: clamp(0.75rem, 1.5vw, 1.125rem);
    --small-size: clamp(0.65rem, 1vw, 0.875rem);

    --slide-padding: clamp(1rem, 4vw, 4rem);
    --content-gap: clamp(0.5rem, 2vw, 2rem);
    --element-gap: clamp(0.25rem, 1vw, 1rem);
}

.card, .container, .content-box {
    max-width: min(90vw, 1000px);
    max-height: min(80vh, 700px);
}

.feature-list, .bullet-list {
    gap: clamp(0.4rem, 1vh, 1rem);
}

.feature-list li, .bullet-list li {
    font-size: var(--body-size);
    line-height: 1.4;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr));
    gap: clamp(0.5rem, 1.5vw, 1rem);
}

img, .image-container {
    max-width: 100%;
    max-height: min(50vh, 400px);
    object-fit: contain;
}

@media (max-height: 700px) {
    :root {
        --slide-padding: clamp(0.75rem, 3vw, 2rem);
        --content-gap: clamp(0.4rem, 1.5vw, 1rem);
        --title-size: clamp(1.25rem, 4.5vw, 2.5rem);
        --h2-size: clamp(1rem, 3vw, 1.75rem);
    }
}

@media (max-height: 600px) {
    :root {
        --slide-padding: clamp(0.5rem, 2.5vw, 1.5rem);
        --content-gap: clamp(0.3rem, 1vw, 0.75rem);
        --title-size: clamp(1.1rem, 4vw, 2rem);
        --body-size: clamp(0.7rem, 1.2vw, 0.95rem);
    }

    .nav-dots, .keyboard-hint, .decorative {
        display: none;
    }
}

@media (max-height: 500px) {
    :root {
        --slide-padding: clamp(0.4rem, 2vw, 1rem);
        --title-size: clamp(1rem, 3.5vw, 1.5rem);
        --h2-size: clamp(0.9rem, 2.5vw, 1.25rem);
        --body-size: clamp(0.65rem, 1vw, 0.85rem);
    }
}

@media (max-width: 600px) {
    :root {
        --title-size: clamp(1.25rem, 7vw, 2.5rem);
    }

    .grid {
        grid-template-columns: 1fr;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.2s !important;
    }

    html {
        scroll-behavior: auto;
    }
}
```## 视口清单

- 每个“.slide”都有“height：100vh”、“height：100dvh”和“overflow：hidden”
- 所有排版都使用 `clamp()`
- 所有间距均使用“clamp()”或视口单位
- 图像有“最大高度”限制
- 网格适应`auto-fit` + `minmax()`
- 短高度断点存在于`700px`、`600px`和`500px`处
- 如果感觉有什么地方局促，请将幻灯片分开

## 情绪到预设映射

|心情 |良好的预设|
|------|--------------|
|印象深刻/自信|大胆信号、电音工作室、深色植物 |
|兴奋/充满活力|创意电压、霓虹网络、分裂粉彩 |
|冷静/专注|笔记本标签、纸张和墨水，瑞士现代 |
|受到启发/感动|深色植物、复古社论、柔和几何 |

## 预设目录

### 1. 大胆的信号

- Vibe：自信、高影响力、为主题演讲做好准备
- 最适合：推介材料、发布、声明
- 字体：Archivo Black + Space Grotesk
- 调色板：木炭底座、热橙色焦点卡、清晰的白色文字
- 签名：超大部分编号、暗场高对比度卡片

### 2. 电动工作室

- 氛围：干净、大胆、经过机构打磨
- 最适合：客户演示、战略审查
- 字体：仅 Manrope
- 调色板：黑色、白色、饱和钴色
- 签名：两面板分割和清晰的编辑对齐

### 3.创意电压

- Vibe：充满活力、复古现代、俏皮自信
- 最适合：创意工作室、品牌工作、产品故事讲述
- 字体：Syne + Space Mono
- 调色板：电光蓝、霓虹黄、深海军蓝
- 签名：半色调纹理、徽章、强烈对比

### 4. 深色植物

- 氛围：优雅、优质、大气
- 最适合：奢侈品牌、深思熟虑的叙述、优质产品甲板
- 字体：Cormorant + IBM Plex Sans
- 调色板：近黑色、暖象牙色、腮红、金色、赤土色
- 签名：模糊的抽象圆圈、精细的规则、受限的运动

### 5.笔记本选项卡

- 氛围：社论、组织、触觉
- 最适合：报告、评论、结构化讲故事
- 字体：Bodoni Moda + DM Sans
- 调色板：木炭上奶油色纸，带有柔和的标签
- 签名：纸张、彩色侧边标签、活页夹详细信息

### 6. 柔和的几何

- 氛围：平易近人、现代、友好
- 最适合：产品概述、入门、更轻的品牌甲板
- 字体：仅限 Jakarta Sans
- 调色板：淡蓝色、奶油色卡片、柔和的粉色/薄荷/薰衣草色调
- 签名：垂直药丸、圆形卡片、柔和阴影

### 7.分裂粉彩

- 氛围：俏皮、现代、创意
- 最适合：机构介绍、研讨会、作品集
- 字体：仅限服装
- 调色板：桃色 + 薰衣草色，带有薄荷徽章
- 签名：分割背景、圆形标签、光栅覆盖

### 8.复古社论

- 氛围：机智、个性驱动、受杂志启发
- 最适合：个人品牌、固执己见的演讲、讲故事
- 字体：Fraunces + Work Sans
- 调色板：奶油色、木炭色、尘土色温暖色调
- 签名：几何口音、边框标注、有力的衬线标题

### 9. 霓虹网络

- 氛围：未来、科技、动感
- 最适合：人工智能、基础设施、开发工具、X 未来演讲
- 字体：Clash Display + Satoshi
- 调色板：午夜海军蓝、青色、洋红色
- 特征：辉光、粒子、网格、数据雷达能量

### 10. 航站楼绿色

- Vibe：以开发人员为中心，防黑客
- 最适合：API、CLI 工具、工程演示
- 字体：仅限 JetBrains Mono
- 调色板：GitHub 深色 + 终端绿色
- 签名：扫描线、命令行取景、精确的等宽节奏

### 11.瑞士现代

- Vibe：最小、精确、数据转发
- 最适合：企业、产品策略、分析
- 字体：Archivo + Nunito
- 调色板：白色、黑色、信号红
- 特征：可见网格、不对称、几何规律

### 12. 纸张和墨水

- 氛围：文学、深思熟虑、故事驱动
- 最适合：论文、主题叙述、宣言
- 字体：Cormorant Garamond + Source Serif 4
- 调色板：暖奶油色、木炭色、深红色调
- 签名：引文、首字下沉、优雅的规则

## 直接选择提示

如果用户已经知道他们想要的样式，让他们直接从上面的预设名称中选择，而不是强制生成预览。

## 动画感觉映射

|感觉|运动方向 |
|--------------------|--------------------|
|戏剧/电影|缓慢淡入淡出、视差、大比例放大 |
|科技/未来派 |发光、粒子、网格运动、打乱文本 |
|俏皮/友善|弹性缓动、圆形形状、浮动运动 |
|专业/企业|微妙的 200-300 毫秒过渡，干净的幻灯片 |
|平静/简约|非常克制的运动，空白优先 |
|社论/杂志|层次感强，文字与图像交错互动|

## CSS 陷阱：否定函数

永远不要写这些：```css
right: -clamp(28px, 3.5vw, 44px);
margin-left: -min(10vw, 100px);
```浏览器会默默地忽略它们。

总是这样写：```css
right: calc(-1 * clamp(28px, 3.5vw, 44px));
margin-left: calc(-1 * min(10vw, 100px));
```## 验证大小

至少测试：
- 桌面：`1920x1080`、`1440x900`、`1280x720`
- 平板电脑：`1024x768`、`768x1024`
- 移动设备：`375x667`、`414x896`
- 横向手机：`667x375`、`896x414`

## 反模式

不要使用：
- 白底紫色启动模板
- Inter / Roboto / Arial 作为视觉声音，除非用户明确希望功利主义中立
- 弹幕、小型字体或需要滚动的代码块
- 当抽象几何能更好地完成工作时，装饰性插图