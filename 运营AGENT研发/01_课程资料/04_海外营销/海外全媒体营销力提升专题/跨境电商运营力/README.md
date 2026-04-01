# 三节课课程逐字稿提取指南

## 任务概述
从三节课网站下载以下课程的逐字稿：
1. 全球流量入口Google (13节)
2. 如何拉高营销ROI
3. TikTok引流增长方法论

## 保存目录结构
```
/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/
├── 全球流量入口Google (13节)/
│   └── 逐字稿/
│       ├── 01-课程引入.md
│       ├── 02-第一章：Google为何能常年占据全球流量霸主地位？.md
│       └── ...
├── 如何拉高营销ROI/
│   └── 逐字稿/
│       └── ...
└── TikTok引流增长方法论/
    └── 逐字稿/
        └── ...
```

## 手动提取步骤

### 方法一：使用Playwright MCP自动化提取

1. 访问课程页面：https://www.sanjieke.cn/path_detail/1189

2. 找到目标课程并点击进入

3. 在课程学习页面：
   - 点击"文稿"标签
   - 复制逐字稿内容
   - 点击下一章节
   - 重复操作

### 方法二：使用浏览器开发者工具

1. 打开浏览器开发者工具 (F12)

2. 进入Network标签

3. 访问课程学习页面

4. 查找包含逐字稿内容的API请求

5. 导出数据为JSON格式

6. 转换为Markdown文件

### 方法三：使用浏览器控制台脚本

在课程学习页面的浏览器控制台中运行以下脚本：

```javascript
// 提取当前章节逐字稿
function extractTranscript() {
    const paragraphs = [];
    let inTranscript = false;

    document.querySelectorAll('p').forEach(p => {
        const text = p.textContent.trim();
        if (text === '同学你好') {
            inTranscript = true;
        }
        if (inTranscript && text && text.length > 5) {
            paragraphs.push(text);
        }
        if (text.includes('大家都在问')) {
            inTranscript = false;
        }
    });

    return {
        title: document.querySelector('[class*="course-title"]')?.textContent || '未知章节',
        content: paragraphs.join('\n\n')
    };
}

// 提取所有章节
async function extractAllChapters() {
    const chapters = [];
    const chapterElements = document.querySelectorAll('[class*="outline"] li');

    for (let i = 0; i < chapterElements.length; i++) {
        chapterElements[i].click();
        await new Promise(resolve => setTimeout(resolve, 2000));

        const transcript = extractTranscript();
        chapters.push({
            index: i + 1,
            ...transcript
        });
    }

    return chapters;
}

// 运行提取
extractAllChapters().then(data => {
    console.log(JSON.stringify(data, null, 2));

    // 下载为JSON文件
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'transcripts.json';
    a.click();
});
```

## 注意事项

1. 确保已登录三节课账号
2. 确保有权限访问这些课程
3. 逐字稿内容可能包含OCR识别错误，建议人工校对
4. 文件名中的特殊字符会被自动清理
5. 每个章节的逐字稿将保存为独立的Markdown文件

## 联系方式

如有问题，请联系技术支持。