#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索并下载"品牌出海DTC电商独立站"课程逐字稿

使用方法:
1. 确保已安装依赖: pip3 install requests playwright
2. 运行: python3 search_and_download_dtc.py
3. 如果需要登录，在浏览器窗口中登录后按回车继续
"""

import requests
import json
import os
import re
import asyncio
from playwright.async_api import async_playwright

BASE_API = "https://web-api.sanjieke.cn"
TARGET_COURSE = "品牌出海DTC电商独立站"
SAVE_DIR = "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/品牌出海DTC电商独立站/逐字稿"

def search_courses(keyword):
    """搜索课程"""
    url = f"{BASE_API}/b-side/api/web/search/query"
    params = {'keyword': keyword, 'type': 'course', 'page': 1, 'pageSize': 50}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.sanjieke.cn/'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                return data.get('data', {}).get('list', [])
    except Exception as e:
        print(f"搜索失败: {e}")
    return []

def get_path_courses(path_id):
    """获取学习路径中的课程"""
    url = f"{BASE_API}/b-side/api/web/path/path_id/{path_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                return data.get('data', {}).get('courses', [])
    except Exception as e:
        print(f"获取路径失败: {e}")
    return []

def get_course_outline(product_id):
    """获取课程大纲"""
    url = f"{BASE_API}/b-side/api/web/product/product_id/{product_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                return data.get('data', {}).get('outlineData', [])
    except Exception as e:
        print(f"获取大纲失败: {e}")
    return []

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

async def get_transcript(page, product_id, node_id):
    """获取课时逐字稿"""
    try:
        # 方法1: 通过API获取
        content_api = f"https://web-api.sanjieke.cn/b-side/api/web/study/0/{product_id}/content/{node_id}"
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

        # 方法2: 访问页面提取
        url = f"https://www.sanjieke.cn/lesson/0/{product_id}/{node_id}"
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
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
                const pTags = Array.from(document.querySelectorAll('p'));
                const texts = pTags.map(p => p.textContent.trim()).filter(t => t && t.length > 5);
                if (texts.length > 3) {
                    return texts.join('\\n\\n');
                }
                return null;
            }
        ''')

        if content:
            return content

        return None

    except Exception as e:
        print(f"    获取逐字稿出错: {e}")
        return None

async def save_transcript(index, title, content):
    """保存逐字稿"""
    os.makedirs(SAVE_DIR, exist_ok=True)

    filename = f"{index:02d}-{title}.md"
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filepath = os.path.join(SAVE_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(content)

    return filepath

async def download_course(product_id, lessons, page):
    """下载课程逐字稿"""
    print(f"\n开始下载课程 (ID: {product_id})")
    print(f"课时数量: {len(lessons)}")

    success = 0
    failed = 0

    for i, lesson in enumerate(lessons, 1):
        title = lesson['title']
        node_id = lesson['node_id']

        print(f"\n[{i}/{len(lessons)}] {title}")

        content = await get_transcript(page, product_id, node_id)

        if content:
            filepath = await save_transcript(i, title, content)
            print(f"  ✓ 已保存")
            success += 1
        else:
            print(f"  ✗ 失败")
            failed += 1

        await asyncio.sleep(2)

    return success, failed

async def main():
    print("="*60)
    print(f"搜索并下载: {TARGET_COURSE}")
    print("="*60)

    # 首先尝试API搜索
    print("\n[步骤1] 使用API搜索课程...")

    # 搜索课程
    courses = search_courses(TARGET_COURSE)
    if not courses:
        print("  直接搜索未找到，尝试学习路径...")
        path_courses = get_path_courses("1189")

        if path_courses:
            print(f"  路径中有 {len(path_courses)} 个课程")
            for course in path_courses:
                name = course.get('name', '')
                course_id = course.get('id', '')
                if "DTC" in name and "独立站" in name:
                    print(f"  ✓ 找到目标课程: {name} (ID: {course_id})")
                    courses = [{'id': course_id, 'name': name}]
                    break

    if not courses:
        print("\nAPI搜索未找到课程，将使用浏览器...")
        print("这可能需要您手动登录并搜索课程")

    # 使用浏览器下载
    print("\n[步骤2] 启动浏览器...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 访问主页
        await page.goto("https://www.sanjieke.cn", wait_until="domcontentloaded", timeout=30000)

        # 检查登录
        if "login" in page.url.lower():
            print("\n需要登录! 请在浏览器中登录...")
            input("登录完成后按回车: ")

        product_id = None
        lessons = []

        if courses:
            # 使用API找到的课程
            product_id = str(courses[0]['id'])
            outline = get_course_outline(product_id)

            if outline:
                lessons = [
                    {'title': l.get('name'), 'node_id': str(l.get('node_id'))}
                    for l in outline
                ]
            else:
                # 从页面获取
                await page.goto(f"https://www.sanjieke.cn/course/detail/sjk/{product_id}", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)

                lessons = await page.evaluate('''
                    () => {
                        if (window.__NUXT__ && window.__NUXT__.data) {
                            for (const data of window.__NUXT__.data) {
                                if (data.productData && data.productData.outlineData) {
                                    return data.productData.outlineData.map(item => ({
                                        title: item.name,
                                        node_id: String(item.node_id)
                                    }));
                                }
                            }
                        }
                        return [];
                    }
                ''')
        else:
            # 需要手动查找
            print("\n请在浏览器中:")
            print("1. 搜索并进入课程页面")
            print("2. 等待页面加载完成后，按回车")
            input("\n按回车继续...")

            # 从当前页面提取
            page_data = await page.evaluate('''
                () => {
                    if (window.__NUXT__ && window.__NUXT__.data) {
                        for (const data of window.__NUXT__.data) {
                            if (data.productData) {
                                const productData = data.productData;
                                return {
                                    product_id: String(productData.id),
                                    lessons: productData.outlineData ? productData.outlineData.map(item => ({
                                        title: item.name,
                                        node_id: String(item.node_id)
                                    })) : []
                                };
                            }
                        }
                    }
                    return null;
                }
            ''')

            if page_data:
                product_id = page_data['product_id']
                lessons = page_data['lessons']

        if product_id and lessons:
            print(f"\n找到课程ID: {product_id}")
            print(f"课时数量: {len(lessons)}")

            success, failed = await download_course(product_id, lessons, page)

            print(f"\n{'='*60}")
            print("下载完成!")
            print(f"{'='*60}")
            print(f"成功: {success} 个")
            print(f"失败: {failed} 个")
            print(f"保存目录: {SAVE_DIR}")
        else:
            print("\n未能获取课程信息")

        print("\n按回车关闭浏览器...")
        input()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
