#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找"品牌出海DTC电商独立站"课程的product_id和课时信息
"""

import asyncio
import json
from playwright.async_api import async_playwright

TARGET_COURSE = "品牌出海DTC电商独立站"

async def main():
    print("="*60)
    print(f"正在查找课程: {TARGET_COURSE}")
    print("="*60)

    async with async_playwright() as p:
        # 启动浏览器（非无头模式，方便手动登录）
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 访问三节课首页
        print("\n1. 正在访问三节课首页...")
        await page.goto("https://www.sanjieke.cn", wait_until="networkidle", timeout=30000)

        # 检查是否需要登录
        current_url = page.url
        if "login" in current_url.lower():
            print("\n需要登录！")
            print("请在浏览器窗口中登录，然后按回车继续...")
            input("登录完成后按回车: ")

        # 方法1: 通过搜索功能查找
        print("\n2. 尝试搜索课程...")

        # 等待页面完全加载
        await asyncio.sleep(2)

        # 尝试多种搜索框选择器
        search_found = await page.evaluate('''
            () => {
                // 查找搜索框
                const selectors = [
                    'input[placeholder*="搜索"]',
                    'input[type="search"]',
                    '.search-input',
                    '#search',
                    'input[name="search"]'
                ];

                for (const selector of selectors) {
                    const input = document.querySelector(selector);
                    if (input && input.offsetParent !== null) {
                        input.value = "品牌出海DTC电商独立站";
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));

                        // 尝试触发搜索
                        const form = input.closest('form');
                        if (form) {
                            form.submit();
                        } else {
                            // 尝试按回车键
                            input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
                        }
                        return true;
                    }
                }
                return false;
            }
        ''')

        if search_found:
            print("  已执行搜索，等待结果...")
            await asyncio.sleep(3)
        else:
            print("  未找到搜索框")

        # 提取搜索结果或当前页面的课程信息
        print("\n3. 分析页面内容...")

        page_content = await page.evaluate('''
            () => {
                const results = [];

                // 查找所有课程链接
                const links = Array.from(document.querySelectorAll('a[href*="course"], a[href*="product"]'));

                for (const link of links) {
                    const text = link.textContent.trim();
                    const href = link.getAttribute('href');

                    if (text && href) {
                        // 提取课程ID
                        let courseId = null;
                        const productIdMatch = href.match(/product_id[=/]([^/&]+)/);
                        const courseIdMatch = href.match(/course[/_]detail[/_][^/]+[/](\\d+)/);
                        const idMatch = href.match(/[/_](\\d{7,})/);

                        if (productIdMatch) courseId = productIdMatch[1];
                        else if (courseIdMatch) courseId = courseIdMatch[1];
                        else if (idMatch) courseId = idMatch[1];

                        results.push({
                            text: text.substring(0, 100),
                            href: href.substring(0, 200),
                            courseId: courseId
                        });
                    }
                }

                // 也检查页面中的数据对象
                let pageData = null;
                if (window.__NUXT__) {
                    pageData = { hasNUXT: true };
                }

                return {
                    links: results,
                    pageData: pageData,
                    pageTitle: document.title,
                    bodyText: document.body.textContent.substring(0, 500)
                };
            }
        ''')

        # 查找匹配的课程
        print("\n4. 查找目标课程...")

        found_courses = []
        for link in page_content['links']:
            text = link['text']
            if TARGET_COURSE in text or ("DTC" in text and "独立站" in text):
                found_courses.append(link)
                print(f"\n  找到匹配:")
                print(f"    标题: {link['text']}")
                print(f"    链接: {link['href']}")
                if link['courseId']:
                    print(f"    课程ID: {link['courseId']}")

        # 如果没找到，显示所有相关链接供用户选择
        if not found_courses:
            print("\n  未自动找到匹配的课程")
            print("\n  相关课程列表:")
            for i, link in enumerate(page_content['links'][:20], 1):
                if '出海' in link['text'] or 'DTC' in link['text'] or '独立站' in link['text']:
                    print(f"    {i}. {link['text']}")
                    if link['courseId']:
                        print(f"       ID: {link['courseId']}")

        # 方法2: 直接访问路径页面
        print("\n5. 尝试访问学习路径页面...")
        await page.goto("https://www.sanjieke.cn/path_detail/1189", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        path_courses = await page.evaluate('''
            () => {
                const courses = [];

                // 从__NUXT__数据中提取
                if (window.__NUXT__ && window.__NUXT__.data) {
                    for (const data of window.__NUXT__.data) {
                        if (data.pathData && data.pathData.courses) {
                            for (const course of data.pathData.courses) {
                                courses.push({
                                    name: course.name,
                                    id: course.id,
                                    products: course.products || []
                                });
                            }
                        }
                    }
                }

                // 从DOM中提取
                const courseElements = document.querySelectorAll('[class*="course"], [class*="product"]');
                for (const el of courseElements) {
                    const links = el.querySelectorAll('a[href*="product"]');
                    for (const link of links) {
                        const href = link.getAttribute('href');
                        const match = href.match(/product_id[=/]([^/&]+)/);
                        if (match) {
                            courses.push({
                                name: link.textContent.trim(),
                                id: match[1]
                            });
                        }
                    }
                }

                return courses;
            }
        ''')

        print(f"\n  路径中的课程:")
        for course in path_courses:
            print(f"    - {course.get('name', '未知')} (ID: {course.get('id', 'N/A')})")

            # 检查是否是目标课程
            if TARGET_COURSE in course.get('name', ''):
                print(f"      ✓ 这是目标课程!")

                # 进入课程详情页获取课时列表
                course_url = f"https://www.sanjieke.cn/course/detail/sjk/{course['id']}"
                print(f"\n6. 正在访问课程详情页...")
                await page.goto(course_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)

                # 获取课时列表
                lessons = await page.evaluate('''
                    () => {
                        const lessons = [];

                        // 从__NUXT__数据中提取
                        if (window.__NUXT__ && window.__NUXT__.data) {
                            for (const data of window.__NUXT__.data) {
                                if (data.productData && data.productData.outlineData) {
                                    return data.productData.outlineData.map(item => ({
                                        node_id: item.node_id,
                                        name: item.name,
                                        type: item.type
                                    }));
                                }
                            }
                        }

                        return lessons;
                    }
                ''')

                print(f"\n  找到 {len(lessons)} 个课时:")
                for i, lesson in enumerate(lessons, 1):
                    print(f"    {i}. {lesson['name']} (Node ID: {lesson['node_id']})")

                # 保存课程信息
                course_info = {
                    "name": TARGET_COURSE,
                    "product_id": course['id'],
                    "lessons": lessons
                }

                info_file = "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/dtc_course_info.json"
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(course_info, f, ensure_ascii=False, indent=2)

                print(f"\n  课程信息已保存到: {info_file}")

                # 生成下载脚本
                download_script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动下载{TARGET_COURSE}课程逐字稿"""

import asyncio
import sys
sys.path.append("/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力")

from download_specific_transcripts import download_course, get_transcript_from_page, save_transcript

COURSE_INFO = {json.dumps(course_info, ensure_ascii=False, indent=4)}

async def main():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        result = await download_course(COURSE_INFO, page)

        await browser.close()

        print(f"\\n下载完成! 成功: {{result['success']}}, 失败: {{result['failed']}}")

if __name__ == "__main__":
    asyncio.run(main())
'''

                script_file = "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/download_dtc_auto.py"
                with open(script_file, 'w', encoding='utf-8') as f:
                    f.write(download_script)

                print(f"  下载脚本已保存到: {script_file}")
                print(f"  运行命令: python3 {script_file}")

        # 保持浏览器打开，供手动操作
        print("\n" + "="*60)
        print("浏览器将保持打开状态")
        print("您可以手动浏览网站查找课程信息")
        print("完成后关闭浏览器窗口...")
        print("="*60)

        # 等待用户关闭浏览器
        await browser.wait_for_event("close")

if __name__ == "__main__":
    asyncio.run(main())
