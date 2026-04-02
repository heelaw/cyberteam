/**
 * 三节课课程逐字稿提取脚本
 * 在浏览器控制台中运行此脚本以提取课程逐字稿
 */

// 主提取函数
async function extractCourseTranscripts() {
    console.log('开始提取课程逐字稿...');

    const transcripts = [];
    let chapterCount = 0;

    // 获取所有章节
    const getChapters = () => {
        const chapters = [];
        document.querySelectorAll('[class*="outline"] li').forEach((el, index) => {
            const p = el.querySelector('p');
            if (p) {
                chapters.push({
                    index: index + 1,
                    title: p.textContent.trim(),
                    element: el
                });
            }
        });
        return chapters;
    };

    // 等待函数
    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // 提取当前页面逐字稿
    const extractCurrentTranscript = () => {
        const content = [];
        let inTranscript = false;

        document.querySelectorAll('p').forEach(p => {
            const text = p.textContent.trim();

            // 识别逐字稿开始
            if (text === '同学你好' || text.startsWith('课程导入')) {
                inTranscript = true;
            }

            // 收集逐字稿内容
            if (inTranscript && text && text.length > 5) {
                content.push(text);
            }

            // 识别逐字稿结束
            if (text.includes('大家都在问') || text.includes('向讲师提问')) {
                inTranscript = false;
            }
        });

        return content.join('\n\n');
    };

    // 获取章节列表
    const chapters = getChapters();
    console.log(`找到 ${chapters.length} 个章节`);

    // 遍历每个章节
    for (let i = 0; i < chapters.length; i++) {
        const chapter = chapters[i];
        console.log(`正在提取第 ${chapter.index} 章: ${chapter.title}`);

        // 点击章节
        chapter.element.click();
        await wait(3000);

        // 确保在"文稿"标签
        const transcriptTab = document.querySelector('a[href="#"]');
        if (transcriptTab && transcriptTab.textContent.includes('文稿')) {
            transcriptTab.click();
            await wait(2000);
        }

        // 提取逐字稿
        const content = extractCurrentTranscript();

        if (content && content.length > 100) {
            transcripts.push({
                chapter: chapter.index,
                title: chapter.title,
                content: content
            });
            chapterCount++;
        } else {
            console.warn(`第 ${chapter.index} 章逐字稿提取失败或内容为空`);
        }
    }

    console.log(`提取完成！共提取 ${chapterCount} 个章节的逐字稿`);
    return transcripts;
}

// 下载函数
function downloadTranscripts(transcripts, courseName) {
    // 创建Markdown内容
    let markdown = `# ${courseName}\n\n`;

    transcripts.forEach(chapter => {
        markdown += `## 第${chapter.chapter}章: ${chapter.title}\n\n`;
        markdown += `${chapter.content}\n\n`;
        markdown += `---\n\n`;
    });

    // 下载为Markdown文件
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${courseName}-逐字稿.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    // 同时下载JSON格式
    const jsonBlob = new Blob([JSON.stringify(transcripts, null, 2)], { type: 'application/json' });
    const jsonUrl = URL.createObjectURL(jsonBlob);
    const jsonA = document.createElement('a');
    jsonA.href = jsonUrl;
    jsonA.download = `${courseName}-逐字稿.json`;
    document.body.appendChild(jsonA);
    jsonA.click();
    document.body.removeChild(jsonA);
    URL.revokeObjectURL(jsonUrl);

    console.log('文件已下载！');
}

// 使用说明
console.log(`
====================================
三节课逐字稿提取脚本
====================================

使用方法：
1. 打开课程学习页面
2. 打开浏览器控制台 (F12)
3. 复制并粘贴此脚本
4. 运行命令：extractCourseTranscripts().then(data => downloadTranscripts(data, '课程名称'))

注意事项：
- 脚本会自动遍历所有章节
- 每个章节会等待3秒加载
- 完成后会自动下载Markdown和JSON文件
- 请确保已登录并有权访问课程

====================================
`);

// 导出函数
window.extractCourseTranscripts = extractCourseTranscripts;
window.downloadTranscripts = downloadTranscripts;
