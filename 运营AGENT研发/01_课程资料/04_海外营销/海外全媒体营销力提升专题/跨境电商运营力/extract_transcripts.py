#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三节课课程逐字稿提取脚本
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

# 目标课程列表
TARGET_COURSES = [
    {
        "name": "全球流量入口Google (13节)",
        "keyword": "全球流量入口：挖掘Google搜索及广告流量池",
        "save_dir": os.path.join(SAVE_BASE_DIR, "全球流量入口Google (13节)", "逐字稿")
    },
    {
        "name": "如何拉高营销ROI",
        "keyword": "如何拉高营销ROI：战略、业务、财务一本账",
        "save_dir": os.path.join(SAVE_BASE_DIR, "如何拉高营销ROI", "逐字稿")
    },
    {
        "name": "TikTok引流增长方法论",
        "keyword": "TikTok引流增长方法论",
        "save_dir": os.path.join(SAVE_BASE_DIR, "TikTok引流增长方法论", "逐字稿")
    }
]

async def extract_transcript_from_page(page):
    """从当前页面提取逐字稿内容"""
    try:
        # 等待页面加载
        await asyncio.sleep(2)

        # 点击"文稿"标签
        await page.click('text=文稿')
        await asyncio.sleep(2)

        # 提取逐字稿内容
        transcript_content = await page.evaluate('''
            () => {
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

                return paragraphs.join('\\n\\n');
            }
        ''')

        return transcript_content
    except Exception as e:
        print(f"提取逐字稿时出错: {e}")
        return None

async def get_chapter_list(page):
    """获取课程章节列表"""
    try:
        chapters = await page.evaluate('''
            () => {
                const chapterElements = document.querySelectorAll('[class*="outline"] li');
                const chapters = [];

                chapterElements.forEach((el, index) => {
                    const p = el.querySelector('p');
                    if (p) {
                        chapters.push({
                            index: index + 1,
                            title: p.textContent.trim()
                        });
                    }
                });

                return chapters;
            }
        ''')
        return chapters
    except Exception as e:
        print(f"获取章节列表时出错: {e}")
        return []

async def save_transcript(course_name, chapter_index, chapter_title, content, save_dir):
    """保存逐字稿到文件"""
    # 确保目录存在
    os.makedirs(save_dir, exist_ok=True)

    # 创建文件名
    filename = f"{chapter_index:02d}-{chapter_title}.md"
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
    print(f"\n开始处理课程: {course_info['name']}")

    # 创建保存目录
    os.makedirs(course_info['save_dir'], exist_ok=True)

    # 查找并点击课程
    await page.evaluate(f'''
        () => {{
            const allLinks = Array.from(document.querySelectorAll('a'));
            for (const link of allLinks) {{
                const pElement = link.querySelector('p');
                if (pElement && pElement.textContent.includes('{course_info['keyword']}')) {{
                    link.click();
                    return true;
                }}
            }}
            return false;
        }}
    ''')

    # 等待页面加载
    await asyncio.sleep(5)

    # 获取章节列表
    chapters = await get_chapter_list(page)
    print(f"找到 {len(chapters)} 个章节")

    # 遍历所有章节
    for i, chapter in enumerate(chapters):
        print(f"正在处理第 {i+1} 章: {chapter['title']}")

        # 点击章节
        await page.evaluate(f'''
            () => {{
                const chapters = document.querySelectorAll('[class*="outline"] li');
                if (chapters[{i}]) {{
                    chapters[{i}].click();
                }}
            }}
        ''')

        # 等待页面加载
        await asyncio.sleep(3)

        # 提取逐字稿
        content = await extract_transcript_from_page(page)

        if content:
            # 保存逐字稿
            await save_transcript(
                course_info['name'],
                chapter['index'],
                chapter['title'],
                content,
                course_info['save_dir']
            )
        else:
            print(f"无法提取第 {i+1} 章的逐字稿")

async def main():
    """主函数"""
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 访问课程列表页面
        print(f"访问课程列表页面: {BASE_URL}")
        await page.goto(BASE_URL)
        await asyncio.sleep(3)

        # 处理每门课程
        for course in TARGET_COURSES:
            try:
                await process_course(page, course)
                # 返回课程列表页面
                await page.goto(BASE_URL)
                await asyncio.sleep(3)
            except Exception as e:
                print(f"处理课程 {course['name']} 时出错: {e}")
                continue

        # 关闭浏览器
        await browser.close()
        print("\n所有课程处理完成！")

if __name__ == "__main__":
    asyncio.run(main())
