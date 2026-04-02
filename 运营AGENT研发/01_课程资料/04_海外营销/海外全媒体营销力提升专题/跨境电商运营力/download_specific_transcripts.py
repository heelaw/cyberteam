#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三节课特定课程逐字稿提取脚本
直接使用product_id和node_id获取逐字稿
"""

import asyncio
import json
import os
import re
from playwright.async_api import async_playwright

# 课程1: 如何拉高营销ROI
COURSE_1 = {
    "name": "如何拉高营销ROI",
    "product_id": "8003104",
    "save_dir": "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/如何拉高营销ROI/逐字稿",
    "lessons": [
        {"title": "课程导读", "node_id": "34979151"},
        {"title": "第二章 市场预算管理：总目标、分渠道", "node_id": "34544006"},
        {"title": "第三章 市场预算管理：分玩法、分产品", "node_id": "34544007"},
        {"title": "第四章 市场预算管理：分阶段", "node_id": "34544008"},
        {"title": "课程总结", "node_id": "34979152"}
    ]
}

# 课程2: 品牌出海私域营销 - 需要先获取课程ID和课时列表
COURSE_2 = {
    "name": "品牌出海私域营销",
    "keyword": "品牌出海私域营销",
    "save_dir": "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/品牌出海私域营销/逐字稿",
    "product_id": None,  # 需要查找
    "lessons": []  # 需要获取
}

async def get_transcript_from_page(page, product_id, node_id):
    """从页面提取逐字稿内容"""
    try:
        url = f"https://www.sanjieke.cn/lesson/0/{product_id}/{node_id}"
        print(f"  访问: {url}")

        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)

        # 尝试点击"文稿"按钮
        try:
            # 查找并点击文稿按钮
            transcript_clicked = await page.evaluate('''
                () => {
                    // 查找文稿按钮
                    const buttons = Array.from(document.querySelectorAll('button, div, span'));
                    for (const btn of buttons) {
                        if (btn.textContent.includes('文稿') || btn.textContent.includes('逐字稿')) {
                            btn.click();
                            return true;
                        }
                    }

                    // 检查是否已经有文稿内容显示
                    const transcriptSections = document.querySelectorAll('[class*="transcript"], [class*="manuscript"], [class*="text-content"]');
                    return transcriptSections.length > 0;
                }
            ''')

            if transcript_clicked:
                await asyncio.sleep(2)
        except Exception as e:
            print(f"  点击文稿按钮时出错: {e}")

        # 提取文稿内容
        transcript_data = await page.evaluate('''
            () => {
                // 方法1: 查找包含文稿的容器
                const possibleContainers = [
                    // 常见的文稿容器选择器
                    '[class*="transcript"]',
                    '[class*="manuscript"]',
                    '[class*="subtitle"]',
                    '[class*="caption"]',
                    '[class*="text-content"]',
                    // 三节课特定的选择器
                    '.lesson-manuscript',
                    '.course-manuscript',
                    '.manuscript-content',
                    '.transcript-content',
                    // 通用内容区域
                    '[class*="content"]',
                    'article',
                    '.article-content'
                ];

                for (const selector of possibleContainers) {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        const text = el.textContent || el.innerText;
                        if (text && text.length > 100 && !text.includes('登录')) {
                            // 清理文本
                            let cleanText = text.trim();
                            // 移除重复的空白字符
                            cleanText = cleanText.replace(/\\s+/g, ' ');
                            return { found: true, text: cleanText, method: 'container-' + selector };
                        }
                    }
                }

                // 方法2: 从页面数据中提取
                if (window.__NUXT__) {
                    const dataStr = JSON.stringify(window.__NUXT__);
                    // 查找字幕或文稿数据
                    const subMatch = dataStr.match(/"subtitles?"[^[]*\\[([^\\]]+)\\]/);
                    if (subMatch) {
                        return { found: true, text: subMatch[1], method: 'nuxt-subtitle' };
                    }
                }

                return { found: false, text: '', method: 'none' };
            }
        ''')

        if transcript_data['found'] and transcript_data['text']:
            print(f"  找到文稿内容 (方法: {transcript_data['method']})")
            return transcript_data['text']

        # 方法3: 尝试通过API获取字幕
        content_api = f"https://web-api.sanjieke.cn/b-side/api/web/study/0/{product_id}/content/{node_id}"
        try:
            response = await page.request.get(content_api)
            if response.status == 200:
                data = await response.json()
                if data.get('code') == 200:
                    nodes = data.get('data', {}).get('nodes', [])
                    if nodes:
                        node_data = nodes[0]

                        # 检查是否有视频字幕
                        if node_data.get('videoContent', {}).get('subtitles'):
                            subtitles = node_data['videoContent']['subtitles']
                            for sub in subtitles:
                                if sub.get('language') == 'ZH_CN' or sub.get('languageName', '').startswith('中文'):
                                    sub_url = sub.get('url')
                                    if sub_url:
                                        sub_response = await page.request.get(sub_url)
                                        if sub_response.status == 200:
                                            vtt_content = await sub_response.text()
                                            return parse_vtt_to_text(vtt_content)

                        # 检查是否有文稿内容
                        if node_data.get('textContent') or node_data.get('manuscriptContent'):
                            text_content = node_data.get('textContent') or node_data.get('manuscriptContent')
                            if text_content:
                                return text_content
        except Exception as e:
            print(f"  API请求失败: {e}")

        print(f"  未能找到文稿内容")
        return None

    except Exception as e:
        print(f"  获取文稿时出错: {e}")
        return None

def parse_vtt_to_text(vtt_content):
    """将VTT字幕转换为纯文本"""
    lines = vtt_content.split('\n')
    text_parts = []

    for line in lines:
        line = line.strip()
        # 跳过时间戳和空行
        if not line or '-->' in line or line.startswith('WEBVTT'):
            continue
        # 移除HTML标签
        line = re.sub(r'<[^>]+>', '', line)
        # 移除花括号内容
        line = re.sub(r'\{[^}]+\}', '', line)
        if line:
            text_parts.append(line)

    return ' '.join(text_parts)

async def save_transcript(save_dir, index, title, content):
    """保存逐字稿到文件"""
    os.makedirs(save_dir, exist_ok=True)

    # 创建文件名
    filename = f"{index:02d}-{title}.md"
    # 清理文件名中的非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filepath = os.path.join(save_dir, filename)

    # 保存内容
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(content)

    print(f"  ✓ 已保存: {filename}")
    return filepath

async def find_course_2_info(page):
    """查找课程2的product_id和课时列表"""
    print("\n正在查找课程2的信息...")

    # 从已有的目录推断可能的product_id
    # 先检查目录中是否有相关文件

    # 访问搜索页面或直接尝试访问已知课程
    search_url = "https://www.sanjieke.cn/path_detail/1189"
    await page.goto(search_url, wait_until="networkidle", timeout=30000)
    await asyncio.sleep(3)

    # 搜索课程
    course_info = await page.evaluate('''
        () => {
            const keyword = "品牌出海私域营销";
            const allLinks = Array.from(document.querySelectorAll('a'));

            for (const link of allLinks) {
                const text = link.textContent || "";
                if (text.includes(keyword)) {
                    // 从href中提取course_id
                    const href = link.href || "";
                    const match = href.match(/course\\/detail\\/sjk\\/(\\d+)/);
                    if (match) {
                        return {
                            found: true,
                            course_id: match[1],
                            title: text.trim()
                        };
                    }
                }
            }

            return { found: false, course_id: null, title: null };
        }
    ''')

    if course_info['found']:
        print(f"  找到课程: {course_info['title']}")
        print(f"  课程ID: {course_info['course_id']}")

        # 点击进入课程详情页获取课时列表
        await page.evaluate(f'''
            () => {{
                const keyword = "品牌出海私域营销";
                const allLinks = Array.from(document.querySelectorAll('a'));
                for (const link of allLinks) {{
                    if (link.textContent.includes(keyword)) {{
                        link.click();
                        return true;
                    }}
                }}
                return false;
            }}
        ''')

        await asyncio.sleep(3)

        # 获取课时列表
        lessons_data = await page.evaluate('''
            () => {
                if (window.__NUXT__ && window.__NUXT__.data && window.__NUXT__.data[0]) {
                    const productData = window.__NUXT__.data[0].productData;
                    if (productData && productData.outlineData) {
                        return productData.outlineData.map(item => ({
                            node_id: item.node_id,
                            name: item.name,
                            type: item.type
                        }));
                    }
                }
                return [];
            }
        ''')

        print(f"  找到 {len(lessons_data)} 个课时")
        return course_info['course_id'], lessons_data

    print("  未找到课程，尝试备用方法...")

    # 备用方法：尝试已知的product_id
    possible_ids = ["8003105", "8003106", "8003107"]  # 根据已有课程ID推测
    for pid in possible_ids:
        test_url = f"https://www.sanjieke.cn/course/detail/sjk/{pid}"
        await page.goto(test_url, wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(2)

        is_correct = await page.evaluate('''
            () => {
                return document.title.includes("私域") ||
                       document.body.textContent.includes("品牌出海私域营销");
            }
        ''')

        if is_correct:
            print(f"  找到课程ID: {pid}")

            lessons_data = await page.evaluate('''
                () => {
                    if (window.__NUXT__ && window.__NUXT__.data && window.__NUXT__.data[0]) {
                        const productData = window.__NUXT__.data[0].productData;
                        if (productData && productData.outlineData) {
                            return productData.outlineData.map(item => ({
                                node_id: item.node_id,
                                name: item.name,
                                type: item.type
                            }));
                        }
                    }
                    return [];
                }
            ''')

            return pid, lessons_data

    return None, []

async def download_course(course_info, page):
    """下载单个课程的所有课时"""
    print(f"\n{'='*60}")
    print(f"开始下载课程: {course_info['name']}")
    print(f"{'='*60}")

    product_id = course_info['product_id']
    lessons = course_info['lessons']
    save_dir = course_info['save_dir']

    if not product_id:
        print("课程ID为空，跳过")
        return {"success": 0, "failed": 0, "lessons": []}

    print(f"课程ID: {product_id}")
    print(f"课时数量: {len(lessons)}")

    success_count = 0
    failed_count = 0
    downloaded_lessons = []

    for i, lesson in enumerate(lessons, 1):
        title = lesson['title']
        node_id = lesson['node_id']

        print(f"\n[{i}/{len(lessons)}] 正在下载: {title}")
        print(f"  Node ID: {node_id}")

        # 获取逐字稿
        content = await get_transcript_from_page(page, product_id, node_id)

        if content:
            # 保存逐字稿
            filepath = await save_transcript(save_dir, i, title, content)
            success_count += 1
            downloaded_lessons.append({
                "index": i,
                "title": title,
                "node_id": node_id,
                "filepath": filepath
            })
        else:
            failed_count += 1
            downloaded_lessons.append({
                "index": i,
                "title": title,
                "node_id": node_id,
                "filepath": None,
                "error": "未能获取内容"
            })

        # 避免请求过快
        await asyncio.sleep(2)

    return {
        "success": success_count,
        "failed": failed_count,
        "lessons": downloaded_lessons
    }

async def main():
    """主函数"""
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 结果统计
        results = []

        # 下载课程1: 如何拉高营销ROI
        result1 = await download_course(COURSE_1, page)
        results.append({
            "course": COURSE_1['name'],
            "result": result1
        })

        # 查找并下载课程2: 品牌出海私域营销
        print(f"\n{'='*60}")
        print("准备处理课程2: 品牌出海私域营销")
        print(f"{'='*60}")

        course2_id, course2_lessons = await find_course_2_info(page)

        if course2_id and course2_lessons:
            COURSE_2['product_id'] = course2_id
            COURSE_2['lessons'] = [
                {"title": lesson['name'], "node_id": lesson['node_id']}
                for lesson in course2_lessons
            ]

            result2 = await download_course(COURSE_2, page)
            results.append({
                "course": COURSE_2['name'],
                "result": result2
            })
        else:
            print("\n无法找到课程2的信息")
            results.append({
                "course": COURSE_2['name'],
                "result": {"success": 0, "failed": 0, "error": "未找到课程信息"}
            })

        await browser.close()

        # 打印最终统计
        print(f"\n{'='*60}")
        print("下载完成统计")
        print(f"{'='*60}")

        for r in results:
            print(f"\n课程: {r['course']}")
            if 'error' in r['result']:
                print(f"  状态: 失败 - {r['result']['error']}")
            else:
                print(f"  成功: {r['result']['success']} 课时")
                print(f"  失败: {r['result']['failed']} 课时")

        print(f"\n{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())
