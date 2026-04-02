#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三节课课程逐字稿提取脚本 - 通过API获取
通过监听API请求获取视频字幕作为逐字稿
"""

import asyncio
import json
import os
import re
from playwright.async_api import async_playwright

# 配置信息
BASE_URL = "https://www.sanjieke.cn/path_detail/1189"
SAVE_BASE_DIR = "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力"

# 目标课程列表
TARGET_COURSES = [
    {
        "name": "B2B出海营销LinkedIn",
        "keyword": "B2B出海营销——如何通过LinkedIn抓住高质量商业决策者？",
        "save_dir": os.path.join(SAVE_BASE_DIR, "B2B出海营销LinkedIn", "逐字稿")
    },
    {
        "name": "品牌出海DTC电商独立站",
        "keyword": "品牌出海如何运营DTC电商独立站？",
        "save_dir": os.path.join(SAVE_BASE_DIR, "品牌出海DTC电商独立站", "逐字稿")
    },
    {
        "name": "品牌全球化之路",
        "keyword": "品牌全球化之路:海外市场研究、拓展与进入策略",
        "save_dir": os.path.join(SAVE_BASE_DIR, "品牌全球化之路", "逐字稿")
    },
    {
        "name": "品牌出海私域营销",
        "keyword": "品牌出海私域营销：引流获客实操手册",
        "save_dir": os.path.join(SAVE_BASE_DIR, "品牌出海私域营销", "逐字稿")
    },
    {
        "name": "海外社媒KOL达人营销指南",
        "keyword": "海外社媒KOL达人营销指南",
        "save_dir": os.path.join(SAVE_BASE_DIR, "海外社媒KOL达人营销指南", "逐字稿")
    },
    {
        "name": "海外社交媒体营销攻略",
        "keyword": "跨境电商必备：海外社交媒体营销攻略",
        "save_dir": os.path.join(SAVE_BASE_DIR, "海外社交媒体营销攻略", "逐字稿")
    }
]

async def get_course_id_and_outline(page, course_keyword):
    """从课程列表页面获取课程ID和章节列表"""
    try:
        # 点击课程链接
        await page.evaluate(f'''
            () => {{
                const allLinks = Array.from(document.querySelectorAll('a'));
                for (const link of allLinks) {{
                    const pElement = link.querySelector('p');
                    if (pElement && pElement.textContent.includes('{course_keyword}')) {{
                        link.click();
                        return true;
                    }}
                }}
                return false;
            }}
        ''')

        await asyncio.sleep(3)

        # 获取课程ID和章节列表
        course_info = await page.evaluate('''
            () => {
                // 从URL中获取课程ID
                const urlMatch = window.location.href.match(/course\\/detail\\/sjk\\/(\\d+)/);
                const courseId = urlMatch ? urlMatch[1] : null;

                // 从页面数据中获取章节列表
                if (window.__NUXT__ && window.__NUXT__.data && window.__NUXT__.data[0]) {
                    const productData = window.__NUXT__.data[0].productData;
                    if (productData && productData.outlineData) {
                        return {
                            courseId: productData.course_id,
                            chapters: productData.outlineData.map(item => ({
                                node_id: item.node_id,
                                name: item.name,
                                type: item.type
                            }))
                        };
                    }
                }

                return { courseId: null, chapters: [] };
            }
        ''')

        return course_info
    except Exception as e:
        print(f"获取课程大纲时出错: {e}")
        return {"courseId": None, "chapters": []}

async def get_subtitle_from_api(page, course_id, node_id):
    """通过API获取视频字幕"""
    try:
        # 访问章节页面
        url = f"https://www.sanjieke.cn/lesson/0/{course_id}/{node_id}"
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)

        # 监听API请求获取字幕
        subtitle_data = await page.evaluate('''
            async () => {
                // 查找字幕数据
                const videoElements = document.querySelectorAll('[data-subtitle], video');
                let subtitleUrl = null;

                // 尝试从网络请求中获取
                return new Promise((resolve) => {
                    const originalFetch = window.fetch;
                    window.fetch = function(...args) {
                        const url = args[0];
                        if (typeof url === 'string' && url.includes('video/text')) {
                            resolve({ url: url, found: true });
                            window.fetch = originalFetch;
                        }
                        return originalFetch.apply(this, args);
                    };

                    // 如果没有找到，尝试从页面数据获取
                    setTimeout(() => {
                        const scripts = Array.from(document.querySelectorAll('script'));
                        for (const script of scripts) {
                            const text = script.textContent;
                            if (text && text.includes('video/text')) {
                                const match = text.match(/https:[^"']*video[^""]*subtitle[^""]*[^"']*/);
                                if (match) {
                                    resolve({ url: match[0], found: true });
                                    return;
                                }
                            }
                        }
                        resolve({ url: null, found: false });
                    }, 2000);
                });
            }
        ''')

        if subtitle_data.get('found') and subtitle_data.get('url'):
            # 直接请求字幕API
            subtitle_url = subtitle_data['url']
            response = await page.request.get(subtitle_url)
            if response.status == 200:
                data = await response.json()
                if data.get('code') == 200 and data.get('data', {}).get('list'):
                    return data['data']['list']

        # 备用方法：从页面内容API获取
        content_api = f"https://web-api.sanjieke.cn/b-side/api/web/study/0/{course_id}/content/{node_id}"
        response = await page.request.get(content_api)
        if response.status == 200:
            data = await response.json()
            if data.get('code') == 200:
                nodes = data.get('data', {}).get('nodes', [])
                if nodes and nodes[0].get('videoContent', {}).get('subtitles'):
                    subtitles = nodes[0]['videoContent']['subtitles']
                    if subtitles:
                        # 获取中文字幕
                        for sub in subtitles:
                            if sub.get('language') == 'ZH_CN' or sub.get('languageName', '').startswith('中文'):
                                # 请求字幕文件
                                sub_url = sub.get('url')
                                if sub_url:
                                    sub_response = await page.request.get(sub_url)
                                    if sub_response.status == 200:
                                        vtt_content = await sub_response.text()
                                        return parse_vtt(vtt_content)

        return None
    except Exception as e:
        print(f"获取字幕时出错: {e}")
        return None

def parse_vtt(vtt_content):
    """解析VTT字幕文件"""
    lines = vtt_content.split('\n')
    subtitles = []

    current_text = []
    for line in lines:
        line = line.strip()
        if not line:
            if current_text:
                text = ' '.join(current_text)
                if text and not text.startswith('WEBVTT'):
                    subtitles.append(text)
                current_text = []
        elif '-->' not in line and not line.startswith('WEBVTT'):
            # 清理字幕文本
            text = re.sub(r'<[^>]+>', '', line)  # 移除HTML标签
            text = re.sub(r'\{[^}]+\}', '', text)  # 移除花括号内容
            if text:
                current_text.append(text)

    return subtitles

async def save_transcript(course_name, chapter_index, chapter_title, subtitle_lines, save_dir):
    """保存逐字稿到文件"""
    os.makedirs(save_dir, exist_ok=True)

    # 创建文件名
    filename = f"{chapter_index}-{chapter_title}.md"
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filepath = os.path.join(save_dir, filename)

    # 保存内容
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {chapter_title}\n\n")
        for line in subtitle_lines:
            f.write(line + '\n')

    print(f"已保存: {filepath}")

async def process_course(page, course_info):
    """处理单个课程"""
    print(f"\n开始处理课程: {course_info['name']}")

    os.makedirs(course_info['save_dir'], exist_ok=True)

    # 获取课程ID和章节列表
    course_data = await get_course_id_and_outline(page, course_info['keyword'])

    if not course_data.get('courseId'):
        print(f"无法获取课程 {course_info['name']} 的ID")
        return

    course_id = course_data['courseId']
    chapters = course_data.get('chapters', [])

    print(f"课程ID: {course_id}")
    print(f"找到 {len(chapters)} 个章节")

    # 处理每个章节
    for i, chapter in enumerate(chapters):
        node_id = chapter.get('node_id')
        chapter_title = chapter.get('name', f'第{i+1}章')

        print(f"正在处理第 {i+1} 章: {chapter_title}")

        # 获取字幕
        subtitle_lines = await get_subtitle_from_api(page, course_id, node_id)

        if subtitle_lines:
            await save_transcript(
                course_info['name'],
                i + 1,
                chapter_title,
                subtitle_lines,
                course_info['save_dir']
            )
        else:
            print(f"无法获取第 {i+1} 章的字幕")

async def main():
    """主函数"""
    async with async_playwright() as p:
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
                import traceback
                traceback.print_exc()
                continue

        await browser.close()
        print("\n所有课程处理完成！")

if __name__ == "__main__":
    asyncio.run(main())
