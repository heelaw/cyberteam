#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Playwright浏览器查找并下载"品牌出海DTC电商独立站"课程
"""

import asyncio
import json
import os
import re
from playwright.async_api import async_playwright

TARGET_COURSE = "品牌出海DTC电商独立站"
SAVE_DIR = "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/品牌出海DTC电商独立站/逐字稿"

async def find_and_download():
    """查找并下载课程"""

    async with async_playwright() as p:
        # 使用无头浏览器
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("="*60)
        print(f"正在搜索课程: {TARGET_COURSE}")
        print("="*60)

        # 尝试直接访问可能的课程ID范围
        possible_ids = []

        # 从8000000到8009999的范围
        for i in range(100, 500):
            possible_ids.append(f"8003{i:02d}")
        for i in range(0, 200):
            possible_ids.append(f"80032{i:02d}")

        print(f"\n将尝试 {len(possible_ids)} 个可能的课程ID...")

        found_course = None

        # 尝试每个ID
        for idx, course_id in enumerate(possible_ids):
            if (idx + 1) % 50 == 0:
                print(f"已检查 {idx + 1}/{len(possible_ids)} 个ID...")

            url = f"https://www.sanjieke.cn/course/detail/sjk/{course_id}"
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=10000)
                await asyncio.sleep(0.5)

                # 检查页面内容
                page_text = await page.evaluate('() => document.body.textContent')

                if any(keyword in page_text for keyword in ["DTC", "独立站", "品牌出海"]):
                    # 获取课程名称
                    course_name = await page.evaluate('''
                        () => {
                            // 尝试从多个位置获取课程名
                            const selectors = [
                                'h1',
                                '[class*="title"]',
                                '[class*="course-name"]',
                                '.product-title'
                            ];
                            for (const sel of selectors) {
                                const el = document.querySelector(sel);
                                if (el && el.textContent) {
                                    return el.textContent.trim();
                                }
                            }
                            return document.title;
                        }
                    ''')

                    print(f"\n可能找到课程: {course_name} (ID: {course_id})")

                    # 检查是否包含目标关键词
                    if "DTC" in course_name or ("独立站" in course_name and "品牌" in course_name):
                        print(f"✓ 确认这是目标课程!")

                        # 获取课时列表
                        lessons = await page.evaluate('''
                            () => {
                                // 从页面数据中提取
                                if (window.__NUXT__ && window.__NUXT__.data) {
                                    for (const data of window.__NUXT__.data) {
                                        if (data.productData && data.productData.outlineData) {
                                            return data.productData.outlineData.map(item => ({
                                                name: item.name,
                                                node_id: item.node_id
                                            }));
                                        }
                                    }
                                }
                                // 尝试从DOM提取
                                const lessonElements = document.querySelectorAll('[class*="outline"] li, [class*="chapter"] li');
                                const lessons = [];
                                lessonElements.forEach((el, idx) => {
                                    const text = el.textContent.trim();
                                    if (text) {
                                        lessons.push({ name: text, node_id: null });
                                    }
                                });
                                return lessons;
                            }
                        ''')

                        print(f"课时数量: {len(lessons)}")

                        found_course = {
                            'product_id': course_id,
                            'name': course_name,
                            'lessons': lessons
                        }
                        break
            except Exception as e:
                continue

        if not found_course:
            print("\n未找到目标课程")

            # 尝试从学习路径页面获取
            print("尝试从学习路径获取...")
            await page.goto("https://www.sanjieke.cn/path_detail/1189", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)

            path_courses = await page.evaluate('''
                () => {
                    const courses = [];
                    // 从页面中提取课程信息
                    const links = document.querySelectorAll('a[href*="course/detail"]');
                    links.forEach(link => {
                        const href = link.getAttribute('href');
                        const match = href.match(/course\\/detail\\/sjk\\/(\\d+)/);
                        if (match) {
                            courses.push({
                                id: match[1],
                                name: link.textContent.trim()
                            });
                        }
                    });
                    return courses;
                }
            ''')

            print(f"路径中找到 {len(path_courses)} 个课程链接")

            for course in path_courses:
                if "DTC" in course['name'] or ("独立站" in course['name'] and "品牌" in course['name']):
                    print(f"找到目标课程: {course['name']} (ID: {course['id']})")

                    # 访问课程页面获取详细信息
                    await page.goto(f"https://www.sanjieke.cn/course/detail/sjk/{course['id']}", wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(2)

                    lessons = await page.evaluate('''
                        () => {
                            if (window.__NUXT__ && window.__NUXT__.data) {
                                for (const data of window.__NUXT__.data) {
                                    if (data.productData && data.productData.outlineData) {
                                        return data.productData.outlineData.map(item => ({
                                            name: item.name,
                                            node_id: item.node_id
                                        }));
                                    }
                                }
                            }
                            return [];
                        }
                    ''')

                    found_course = {
                        'product_id': course['id'],
                        'name': course['name'],
                        'lessons': lessons
                    }
                    break

        if found_course:
            print(f"\n{'='*60}")
            print(f"找到课程: {found_course['name']}")
            print(f"课程ID: {found_course['product_id']}")
            print(f"课时数量: {len(found_course['lessons'])}")
            print(f"{'='*60}")

            # 开始下载
            print("\n开始下载逐字稿...")

            success = 0
            failed = 0

            for i, lesson in enumerate(found_course['lessons'], 1):
                title = lesson['name']
                node_id = lesson.get('node_id')

                if not node_id:
                    print(f"[{i}/{len(found_course['lessons'])}] 跳过: {title} (无node_id)")
                    failed += 1
                    continue

                print(f"[{i}/{len(found_course['lessons'])}] {title}")

                # 尝试获取逐字稿
                try:
                    # 访问课时页面
                    await page.goto(f"https://www.sanjieke.cn/lesson/0/{found_course['product_id']}/{node_id}", wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(2)

                    # 点击文稿按钮
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

                    # 提取内容
                    content = await page.evaluate('''
                        () => {
                            // 尝试多种方法
                            const methods = [
                                // 从段落标签提取
                                () => {
                                    const pTags = Array.from(document.querySelectorAll('p'));
                                    const texts = pTags.map(p => p.textContent.trim()).filter(t => t && t.length > 5);
                                    if (texts.length > 3) {
                                        return texts.join('\\n\\n');
                                    }
                                    return null;
                                },
                                // 从容器提取
                                () => {
                                    const containers = document.querySelectorAll('[class*="content"], [class*="manuscript"]');
                                    for (const container of containers) {
                                        const text = container.textContent.trim();
                                        if (text.length > 200) {
                                            return text;
                                        }
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

                    if content and len(content) > 50:
                        # 保存文件
                        os.makedirs(SAVE_DIR, exist_ok=True)
                        filename = f"{i:02d}-{title}.md"
                        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                        filepath = os.path.join(SAVE_DIR, filename)

                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(f"# {title}\n\n")
                            f.write(content)

                        print(f"  ✓ 已保存 ({len(content)} 字符)")
                        success += 1
                    else:
                        print(f"  ✗ 未能提取内容")
                        failed += 1

                except Exception as e:
                    print(f"  ✗ 错误: {e}")
                    failed += 1

                await asyncio.sleep(1)

            print(f"\n{'='*60}")
            print("下载完成!")
            print(f"成功: {success} 个")
            print(f"失败: {failed} 个")
            print(f"保存目录: {SAVE_DIR}")
            print(f"{'='*60}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(find_and_download())
