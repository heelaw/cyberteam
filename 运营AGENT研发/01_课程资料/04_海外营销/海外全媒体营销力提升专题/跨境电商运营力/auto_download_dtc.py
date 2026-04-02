#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全自动化下载"品牌出海DTC电商独立站"课程逐字稿
无需交互，自动尝试多种方法获取课程信息
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

# 可能的课程ID列表（根据已有课程推测）
POSSIBLE_IDS = [
    "8003105", "8003106", "8003107", "8003108", "8003109",
    "8003110", "8003111", "8003112", "8003113", "8003114",
    "8003115", "8003116", "8003117", "8003118", "8003119",
    "8003120", "8003200", "8003201", "8003202", "8003203",
]

def get_course_info(product_id):
    """通过API获取课程信息"""
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
                product_data = data.get('data', {})
                return {
                    'id': product_id,
                    'name': product_data.get('name', ''),
                    'outline': product_data.get('outlineData', [])
                }
    except:
        pass
    return None

def find_course():
    """查找目标课程"""
    print("正在搜索目标课程...")

    # 尝试所有可能的ID
    for pid in POSSIBLE_IDS:
        info = get_course_info(pid)
        if info and info['name']:
            print(f"  检查 ID {pid}: {info['name']}")
            if "DTC" in info['name'] or ("独立站" in info['name'] and "品牌" in info['name']):
                print(f"  ✓ 找到目标课程!")
                return info

    print("  未通过API找到，尝试从学习路径获取...")

    # 尝试从学习路径获取
    url = f"{BASE_API}/b-side/api/web/path/path_id/1189"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                courses = data.get('data', {}).get('courses', [])
                for course in courses:
                    name = course.get('name', '')
                    if "DTC" in name and "独立站" in name:
                        course_id = str(course.get('id', ''))
                        print(f"  ✓ 从路径找到: {name} (ID: {course_id})")
                        # 获取详细大纲
                        info = get_course_info(course_id)
                        if info:
                            return info
    except Exception as e:
        print(f"  获取路径失败: {e}")

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

async def get_transcript(page, product_id, node_id):
    """获取课时逐字稿"""
    try:
        # 方法1: 通过API获取字幕
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

        # 方法2: 访问页面提取
        url = f"https://www.sanjieke.cn/lesson/0/{product_id}/{node_id}"
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(1)

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

            if content and len(content) > 50:
                return content
        except:
            pass

        return None

    except Exception as e:
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

async def download_course(course_info, page):
    """下载课程逐字稿"""
    product_id = course_info['id']
    lessons = course_info['outline']

    print(f"\n课程: {course_info['name']}")
    print(f"课程ID: {product_id}")
    print(f"课时数量: {len(lessons)}")

    success = 0
    failed = 0
    results = []

    for i, lesson in enumerate(lessons, 1):
        title = lesson.get('name', f'第{i}章')
        node_id = str(lesson.get('node_id', ''))

        print(f"\n[{i}/{len(lessons)}] {title}")

        if not node_id:
            print(f"  跳过 (无node_id)")
            failed += 1
            results.append({'index': i, 'title': title, 'status': 'skipped'})
            continue

        content = await get_transcript(page, product_id, node_id)

        if content:
            filepath = await save_transcript(i, title, content)
            print(f"  ✓ 已保存 ({len(content)} 字符)")
            success += 1
            results.append({'index': i, 'title': title, 'status': 'success', 'filepath': filepath})
        else:
            print(f"  ✗ 失败")
            failed += 1
            results.append({'index': i, 'title': title, 'status': 'failed'})

        await asyncio.sleep(1)

    return success, failed, results

async def main():
    print("="*60)
    print(f"自动下载: {TARGET_COURSE}")
    print("="*60)

    # 查找课程
    course_info = find_course()

    if not course_info:
        print("\n未能自动找到课程")
        print("请手动提供课程ID")
        return

    print(f"\n找到课程: {course_info['name']}")
    print(f"课时数量: {len(course_info['outline'])}")

    # 使用Playwright下载
    print("\n启动浏览器下载...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        success, failed, results = await download_course(course_info, page)

        await browser.close()

    # 打印结果
    print(f"\n{'='*60}")
    print("下载完成!")
    print(f"{'='*60}")
    print(f"成功: {success} 个")
    print(f"失败: {failed} 个")
    print(f"保存目录: {SAVE_DIR}\n")

    print("文件列表:")
    for r in results:
        status_icon = "✓" if r['status'] == 'success' else ("✗" if r['status'] == 'failed' else "○")
        print(f"  {status_icon} {r['index']:02d}. {r['title']}")

    # 保存结果
    result_file = os.path.join(SAVE_DIR, "download_result.json")
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'course': course_info['name'],
            'success': success,
            'failed': failed,
            'results': results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到: {result_file}")

if __name__ == "__main__":
    asyncio.run(main())
