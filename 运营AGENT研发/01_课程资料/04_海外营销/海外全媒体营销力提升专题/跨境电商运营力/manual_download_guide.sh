#!/bin/bash
# "品牌出海DTC电商独立站"课程逐字稿下载指南
#
# 由于自动化方法未能自动找到课程，请按照以下步骤手动操作：

echo "======================================"
echo "品牌出海DTC电商独立站 - 逐字稿下载指南"
echo "======================================"
echo ""
echo "方法1: 使用浏览器控制台脚本（推荐）"
echo "--------------------------------------"
echo "1. 打开浏览器，访问: https://www.sanjieke.cn"
echo "2. 登录您的账号"
echo "3. 搜索并进入课程: '品牌出海DTC电商独立站'"
echo "4. 进入第一节课的学习页面"
echo "5. 按F12打开开发者工具，切换到Console标签"
echo "6. 复制并粘贴以下脚本："
echo ""
cat <<'SCRIPT'
// 自动提取并下载所有课时的逐字稿
(async function() {
    const transcripts = [];
    let currentLesson = 1;

    async function extractCurrent() {
        // 点击文稿按钮
        const tabs = Array.from(document.querySelectorAll('button, span, a, div'));
        for (const tab of tabs) {
            if (tab.textContent.includes('文稿') || tab.textContent.includes('逐字稿')) {
                tab.click();
                await new Promise(r => setTimeout(r, 1000));
                break;
            }
        }

        // 提取内容
        const paragraphs = Array.from(document.querySelectorAll('p'));
        let content = [];
        for (const p of paragraphs) {
            const text = p.textContent.trim();
            if (text && text.length > 5) {
                content.push(text);
            }
        }

        // 获取标题
        const titleEl = document.querySelector('h1, h2, [class*="title"]');
        const title = titleEl ? titleEl.textContent.trim() : `第${currentLesson}章`;

        return {
            title: title,
            content: content.join('\n\n')
        };
    }

    async function clickNext() {
        const links = Array.from(document.querySelectorAll('a'));
        for (const link of links) {
            if (link.textContent.includes('下一节') || link.textContent.includes('下一章')) {
                link.click();
                return true;
            }
        }
        return false;
    }

    // 主循环
    for (let i = 0; i < 20; i++) {
        console.log(`正在提取第 ${currentLesson} 课...`);

        const transcript = await extractCurrent();
        transcripts.push(transcript);

        console.log(`已提取: ${transcript.title}`);

        const hasNext = await clickNext();
        if (!hasNext) {
            console.log('没有更多课时了');
            break;
        }

        await new Promise(r => setTimeout(r, 3000));
        currentLesson++;
    }

    // 生成Markdown
    const markdown = transcripts.map((t, i) =>
        `# ${i+1}. ${t.title}\n\n${t.content}\n\n---\n\n`
    ).join('\n');

    // 下载文件
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = '品牌出海DTC电商独立站-逐字稿.md';
    a.click();

    console.log(`完成！共提取 ${transcripts.length} 课时`);
    return transcripts;
})();
SCRIPT
echo ""
echo "7. 按回车运行脚本"
echo "8. 等待自动下载完成"
echo ""
echo "======================================"
echo ""
echo "方法2: 手动复制粘贴"
echo "--------------------------------------"
echo "1. 进入课程学习页面"
echo "2. 点击'文稿'标签"
echo "3. 全选并复制逐字稿内容"
echo "4. 保存为Markdown文件"
echo "5. 重复以上步骤完成所有课时"
echo ""
echo "======================================"
echo ""
echo "保存目录: /Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/品牌出海DTC电商独立站/逐字稿/"
echo ""
echo "当前已下载文件:"
ls -la "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/品牌出海DTC电商独立站/逐字稿/"
