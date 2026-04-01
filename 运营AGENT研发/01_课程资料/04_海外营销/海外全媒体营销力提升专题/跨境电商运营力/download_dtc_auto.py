#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动下载"品牌出海DTC电商独立站"课程逐字稿
使用已知的product_id模式来尝试查找课程
"""

import asyncio
import json
import os
import re
from playwright.async_api import async_playwright

# 配置
TARGET_COURSE = "品牌出海DTC电商独立站"
SAVE_DIR = "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/品牌出海DTC电商独立站/逐字稿"

# 根据已有课程的product_id模式，尝试可能的ID
# "如何拉高营销ROI" 的product_id是 "8003104"
# "品牌出海DTC电商独立站" 可能是类似的ID序列
POSSIBLE_PRODUCT_IDS = [
    "8003105", "8003106", "8003107", "8003108", "8003109",
    "8003110", "8003111", "8003112", "8003113", "8003114",
    "8003200", "8003201", "8003202", "8003203", "8003204",
    "8003300", "8003301", "8003302"
]

async def get_transcript_from_page(page, product_id, node_id):
    """从页面提取逐字稿内容"""
    try:
        url = f"https://www.sanjieke.cn/lesson/0/{product_id}/{node_id}"
        print(f"  访问: {url}")

        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # 尝试点击"文稿"按钮
        try:
            await page.evaluate('''
                () => {
                    const buttons = Array.from(document.querySelectorAll('button, div, span, a'));
                    for (const btn of buttons) {
                        if (btn.textContent.includes('文稿') || btn.textContent.includes('逐字稿')) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }
            ''')
            await asyncio.sleep(1)
        except:
            pass

        # 提取文稿内容
        content = await page.evaluate('''
            () => {
                // 尝试多种方法提取内容
                const methods = [
                    // 方法1: 查找包含逐字稿的容器
                    () => {
                        const containers = document.querySelectorAll('[class*="transcript"], [class*="manuscript"], [class*="subtitle"], [class*="text-content"]');
                        for (const container of containers) {
                            const text = container.textContent || container.innerText;
                            if (text && text.length > 200 && !text.includes('登录')) {
                                return text.trim();
                            }
                        }
                        return null;
                    },
                    // 方法2: 查找所有p标签
                    () => {
                        const pTags = Array.from(document.querySelectorAll('p'));
                        const texts = pTags.map(p => p.textContent.trim()).filter(t => t && t.length > 5);
                        if (texts.length > 5) {
                            return texts.join('\\n\\n');
                        }
                        return null;
                    },
                    // 方法3: 查找article或main内容
                    () => {
                        const article = document.querySelector('article, main, [class*="content"]');
                        if (article) {
                            return article.textContent.trim();
                        }
                        return null;
                    }
                ];

                for (const method of methods) {
                    try {
                        const result = method();
                        if (result && result.length > 100) {
                            return result;
                        }
                    } catch (e) {}
                }

                return null;
            }
        ''')

        if content:
            print(f"  ✓ 提取到内容 ({len(content)} 字符)")
            return content

        # 尝试通过API获取
        content_api = f"https://web-api.sanjieke.cn/b-side/api/web/study/0/{product_id}/content/{node_id}"
        try:
            response = await page.request.get(content_api)
            if response.status == 200:
                data = await response.json()
                if data.get('code') == 200:
                    nodes = data.get('data', {}).get('nodes', [])
                    if nodes:
                        node_data = nodes[0]

                        # 检查字幕
                        if node_data.get('videoContent', {}).get('subtitles'):
                            subtitles = node_data['videoContent']['subtitles']
                            for sub in subtitles:
                                if '中文' in sub.get('languageName', '') or sub.get('language') == 'ZH_CN':
                                    sub_url = sub.get('url')
                                    if sub_url:
                                        sub_response = await page.request.get(sub_url)
                                        if sub_response.status == 200:
                                            vtt_content = await sub_response.text()
                                            return parse_vtt_to_text(vtt_content)

                        # 检查文稿
                        if node_data.get('textContent') or node_data.get('manuscriptContent'):
                            return node_data.get('textContent') or node_data.get('manuscriptContent')
        except:
            pass

        print(f"  ✗ 未能提取内容")
        return None

    except Exception as e:
        print(f"  错误: {e}")
        return None

def parse_vtt_to_text(vtt_content):
    """将VTT字幕转换为纯文本"""
    lines = vtt_content.split('\n')
    text_parts = []

    for line in lines:
        line = line.strip()
        if not line or '-->' in line or line.startswith('WEBVTT'):
            continue
        line = re.sub(r'<[^>]+>', '', line)
        line = re.sub(r'\{[^}]+\}', '', line)
        if line:
            text_parts.append(line)

    return ' '.join(text_parts)

async def save_transcript(save_dir, index, title, content):
    """保存逐字稿到文件"""
    os.makedirs(save_dir, exist_ok=True)

    filename = f"{index:02d}-{title}.md"
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filepath = os.path.join(save_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(content)

    return filepath

async def check_course_exists(page, product_id):
    """检查课程是否存在并获取课程信息"""
    try:
        url = f"https://www.sanjieke.cn/course/detail/sjk/{product_id}"
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(2)

        info = await page.evaluate('''
            () => {
                // 检查页面标题和内容
                const title = document.title;
                const bodyText = document.body.textContent;

                // 检查是否是目标课程
                const isTargetCourse = title.includes("DTC") || title.includes("独立站") ||
                                     bodyText.includes("DTC") && bodyText.includes("独立站");

                // 获取课时列表
                let lessons = [];
                if (window.__NUXT__ && window.__NUXT__.data) {
                    for (const data of window.__NUXT__.data) {
                        if (data.productData && data.productData.outlineData) {
                            lessons = data.productData.outlineData.map(item => ({
                                node_id: item.node_id,
                                name: item.name,
                                type: item.type
                            }));
                            break;
                        }
                    }
                }

                return {
                    isTargetCourse: isTargetCourse,
                    title: title,
                    lessonsCount: lessons.length,
                    lessons: lessons
                };
            }
        ''')

        return info

    except Exception as e:
        return None

async def main():
    print("="*60)
    print(f"正在查找并下载课程: {TARGET_COURSE}")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 尝试访问主页
        print("\n访问三节课首页...")
        await page.goto("https://www.sanjieke.cn", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # 检查登录状态
        if "login" in page.url.lower():
            print("\n需要登录！请在浏览器窗口中登录...")
            print("登录后按回车继续...")
            await asyncio.sleep(10)  # 给用户时间登录

        # 尝试可能的product_id
        print(f"\n尝试 {len(POSSIBLE_PRODUCT_IDS)} 个可能的课程ID...")

        found_course = None
        for i, product_id in enumerate(POSSIBLE_PRODUCT_IDS, 1):
            print(f"\n[{i}/{len(POSSIBLE_PRODUCT_IDS)}] 尝试 ID: {product_id}")

            info = await check_course_exists(page, product_id)

            if info:
                print(f"  课程存在: {info['title']}")
                print(f"  课时数量: {info['lessonsCount']}")

                if info['isTargetCourse'] or "DTC" in info['title'] or "独立站" in info['title']:
                    print(f"  ✓ 找到目标课程!")
                    found_course = {
                        'product_id': product_id,
                        'lessons': info['lessons'],
                        'title': info['title']
                    }
                    break

        if not found_course:
            print("\n未自动找到目标课程")
            print("尝试在页面中手动搜索...")

            # 尝试在页面中搜索
            await page.goto("https://www.sanjieke.cn/path_detail/1189", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)

            # 提取路径中的所有课程
            path_courses = await page.evaluate('''
                () => {
                    const courses = [];
                    if (window.__NUXT__ && window.__NUXT__.data) {
                        for (const data of window.__NUXT__.data) {
                            if (data.pathData && data.pathData.courses) {
                                for (const course of data.pathData.courses) {
                                    courses.push({
                                        name: course.name,
                                        id: course.id
                                    });
                                }
                            }
                        }
                    }
                    return courses;
                }
            ''')

            print(f"\n路径中的课程:")
            for course in path_courses:
                print(f"  - {course['name']} (ID: {course['id']})")

                if TARGET_COURSE in course['name']:
                    print(f"    ✓ 这是目标课程!")
                    # 获取课程详情
                    await page.goto(f"https://www.sanjieke.cn/course/detail/sjk/{course['id']}", wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(3)

                    lessons = await page.evaluate('''
                        () => {
                            if (window.__NUXT__ && window.__NUXT__.data) {
                                for (const data of window.__NUXT__.data) {
                                    if (data.productData && data.productData.outlineData) {
                                        return data.productData.outlineData.map(item => ({
                                            node_id: item.node_id,
                                            name: item.name
                                        }));
                                    }
                                }
                            }
                            return [];
                        }
                    ''')

                    found_course = {
                        'product_id': course['id'],
                        'lessons': lessons,
                        'title': course['name']
                    }
                    break

        if found_course:
            print(f"\n{'='*60}")
            print(f"找到课程: {found_course['title']}")
            print(f"课程ID: {found_course['product_id']}")
            print(f"课时数量: {len(found_course['lessons'])}")
            print(f"{'='*60}")

            # 下载逐字稿
            print("\n开始下载逐字稿...")

            success_count = 0
            failed_count = 0
            downloaded = []

            for i, lesson in enumerate(found_course['lessons'], 1):
                title = lesson['name']
                node_id = lesson['node_id']

                print(f"\n[{i}/{len(found_course['lessons'])}] {title}")
                print(f"  Node ID: {node_id}")

                content = await get_transcript_from_page(page, found_course['product_id'], node_id)

                if content:
                    filepath = await save_transcript(SAVE_DIR, i, title, content)
                    print(f"  ✓ 已保存: {os.path.basename(filepath)}")
                    success_count += 1
                    downloaded.append({
                        'index': i,
                        'title': title,
                        'filepath': filepath
                    })
                else:
                    print(f"  ✗ 未能下载")
                    failed_count += 1
                    downloaded.append({
                        'index': i,
                        'title': title,
                        'filepath': None
                    })

                await asyncio.sleep(2)

            # 打印结果
            print(f"\n{'='*60}")
            print("下载完成!")
            print(f"{'='*60}")
            print(f"成功: {success_count} 个")
            print(f"失败: {failed_count} 个")
            print(f"保存目录: {SAVE_DIR}")
            print("\n文件列表:")
            for d in downloaded:
                status = "✓" if d['filepath'] else "✗"
                print(f"  {status} {d['index']}. {d['title']}")

        else:
            print("\n未能找到目标课程")
            print("浏览器将保持打开状态，您可以手动查找...")
            input("按回车关闭浏览器...")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
