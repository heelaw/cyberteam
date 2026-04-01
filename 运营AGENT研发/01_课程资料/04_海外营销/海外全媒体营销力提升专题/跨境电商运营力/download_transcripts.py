#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三节课课程逐字稿提取脚本 - 更新版
用于从三节课网站提取课程的逐字稿内容并保存为markdown文件
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright
import re

# 配置信息
BASE_URL = "https://www.sanjieke.cn/path_detail/1189"
SAVE_BASE_DIR = "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力"

# 目标课程列表 - 包含课程ID和章节ID
TARGET_COURSES = [
    {
        "name": "B2B出海营销LinkedIn",
        "keyword": "B2B出海营销——如何通过LinkedIn抓住高质量商业决策者？",
        "course_id": "34001658",
        "save_dir": os.path.join(SAVE_BASE_DIR, "B2B出海营销LinkedIn", "逐字稿"),
        "chapters": [
            {"id": "34298522", "title": "一、B2B企业出海营销策略及方法"},
            {"id": "34298523", "title": "二、LinkedIn领英职场社交平台为何值得投入？"},
            {"id": "34298524", "title": "三、如何在LinkedIn进行内容营销，与高质量人群沟通？"},
            {"id": "34298525", "title": "四、如何在LinkedIn领英进行广告投放，有效提升收益？"},
            {"id": "34298526", "title": "课程总结"}
        ]
    },
    {
        "name": "品牌出海DTC电商独立站",
        "keyword": "品牌出海如何运营DTC电商独立站？",
        "course_id": "34001765",
        "save_dir": os.path.join(SAVE_BASE_DIR, "品牌出海DTC电商独立站", "逐字稿"),
        "chapters": []  # 需要从页面获取
    },
    {
        "name": "品牌全球化之路",
        "keyword": "品牌全球化之路:海外市场研究、拓展与进入策略",
        "course_id": "34001656",
        "save_dir": os.path.join(SAVE_BASE_DIR, "品牌全球化之路", "逐字稿"),
        "chapters": []  # 需要从页面获取
    },
    {
        "name": "品牌出海私域营销",
        "keyword": "品牌出海私域营销：引流获客实操手册",
        "course_id": "34001766",
        "save_dir": os.path.join(SAVE_BASE_DIR, "品牌出海私域营销", "逐字稿"),
        "chapters": []  # 需要从页面获取
    },
    {
        "name": "海外社媒KOL达人营销指南",
        "keyword": "海外社媒KOL达人营销指南",
        "course_id": "34001657",
        "save_dir": os.path.join(SAVE_BASE_DIR, "海外社媒KOL达人营销指南", "逐字稿"),
        "chapters": []  # 需要从页面获取
    },
    {
        "name": "海外社交媒体营销攻略",
        "keyword": "跨境电商必备：海外社交媒体营销攻略",
        "course_id": "34001659",
        "save_dir": os.path.join(SAVE_BASE_DIR, "海外社交媒体营销攻略", "逐字稿"),
        "chapters": []  # 需要从页面获取
    }
]

async def extract_transcript_from_page(page, url):
    """从指定URL提取逐字稿内容"""
    try:
        print(f"正在访问: {url}")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)

        # 点击"文稿"标签
        try:
            await page.click('.draft-btn', timeout=5000)
            await asyncio.sleep(2)
        except:
            print("未找到文稿按钮，尝试其他方法...")
            # 尝试通过文本点击
            await page.evaluate('''
                () => {
                    const tabs = Array.from(document.querySelectorAll('a, button'));
                    const draftTab = tabs.find(el => el.textContent?.trim() === '文稿');
                    if (draftTab) draftTab.click();
                }
            ''')
            await asyncio.sleep(2)

        # 提取逐字稿内容
        transcript_content = await page.evaluate('''
            () => {
                // 方法1: 查找文稿内容区域
                const selectors = [
                    '.draft-content',
                    '[class*="transcript"]',
                    '[class*="script-content"]',
                    '.lesson-text-content'
                ];

                for (const selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element && element.textContent && element.textContent.length > 100) {
                        return element.textContent.trim();
                    }
                }

                // 方法2: 查找所有段落
                let content = [];
                let inTranscript = false;

                document.querySelectorAll('p').forEach(p => {
                    const text = p.textContent.trim();
                    if (text.includes('同学你好') || text.includes('本节课程')) {
                        inTranscript = true;
                    }
                    if (inTranscript && text && text.length > 5) {
                        content.push(text);
                    }
                    if (text.includes('大家都在问') || text.includes('讲师回复')) {
                        inTranscript = false;
                    }
                });

                if (content.length > 5) {
                    return content.join('\\n\\n');
                }

                // 方法3: 获取所有div的文本
                const allText = document.body.innerText;
                return allText;
            }
        ''')

        return transcript_content
    except Exception as e:
        print(f"提取逐字稿时出错: {e}")
        return None

async def get_course_outline(page, course_id):
    """从课程详情页获取章节列表"""
    try:
        url = f"https://www.sanjieke.cn/course/detail/sjk/{course_id}"
        print(f"正在获取课程大纲: {url}")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        outline = await page.evaluate('''
            () => {
                // 从页面数据中提取大纲
                if (window.__NUXT__ && window.__NUXT__.data && window.__NUXT__.data[0]) {
                    const outlineData = window.__NUXT__.data[0].outlineData;
                    if (outlineData && Array.isArray(outlineData)) {
                        return outlineData.map(item => ({
                            node_id: item.node_id,
                            name: item.name,
                            type: item.type
                        }));
                    }
                }
                return [];
            }
        ''')

        return outline
    except Exception as e:
        print(f"获取课程大纲时出错: {e}")
        return []

async def save_transcript(course_name, chapter_index, chapter_title, content, save_dir):
    """保存逐字稿到文件"""
    # 确保目录存在
    os.makedirs(save_dir, exist_ok=True)

    # 创建文件名
    filename = f"{chapter_index}-{chapter_title}.md"
    # 清理文件名中的非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filepath = os.path.join(save_dir, filename)

    # 保存内容
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {chapter_title}\n\n")
        f.write(content)

    print(f"已保存: {filepath}")

async def process_course(page, course_info):
    """处理单个课程"""
    print(f"\n{'='*60}")
    print(f"开始处理课程: {course_info['name']}")
    print(f"{'='*60}")

    # 创建保存目录
    os.makedirs(course_info['save_dir'], exist_ok=True)

    chapters = course_info.get('chapters', [])

    # 如果没有预定义章节，从课程详情页获取
    if not chapters and course_info.get('course_id'):
        print("正在获取课程章节列表...")
        chapters = await get_course_outline(page, course_info['course_id'])

    if not chapters:
        print(f"警告: 无法获取课程 {course_info['name']} 的章节列表")
        return

    print(f"找到 {len(chapters)} 个章节")

    # 遍历所有章节
    for i, chapter in enumerate(chapters):
        chapter_id = chapter.get('node_id') or chapter.get('id')
        chapter_title = chapter.get('name') or chapter.get('title', f'第{i+1}章')

        print(f"\n正在处理第 {i+1} 章: {chapter_title}")

        # 构建章节URL
        if course_info.get('course_id'):
            url = f"https://www.sanjieke.cn/lesson/0/{course_info['course_id']}/{chapter_id}"
        else:
            print(f"错误: 缺少课程ID，无法构建URL")
            continue

        # 提取逐字稿
        content = await extract_transcript_from_page(page, url)

        if content and len(content) > 100:
            # 保存逐字稿
            await save_transcript(
                course_info['name'],
                i + 1,
                chapter_title,
                content,
                course_info['save_dir']
            )
        else:
            print(f"警告: 无法提取第 {i+1} 章的逐字稿或内容过短")

async def main():
    """主函数"""
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 处理每门课程
        for course in TARGET_COURSES:
            try:
                await process_course(page, course)
            except Exception as e:
                print(f"处理课程 {course['name']} 时出错: {e}")
                import traceback
                traceback.print_exc()
                continue

        # 关闭浏览器
        await browser.close()
        print("\n" + "="*60)
        print("所有课程处理完成！")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
