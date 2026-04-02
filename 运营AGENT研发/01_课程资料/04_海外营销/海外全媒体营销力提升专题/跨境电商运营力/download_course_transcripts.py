#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三节课课程逐字稿下载脚本
通过API直接获取课程信息和字幕
"""

import requests
import json
import os
import re
import time
from urllib.parse import urljoin

# API基础地址
BASE_API = "https://web-api.sanjieke.cn"

# 课程配置
COURSES = [
    {
        "name": "如何拉高营销ROI",
        "product_id": "8003104",
        "save_dir": "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/如何拉高营销ROI/逐字稿",
        "lessons": [
            {"title": "课程导读", "node_id": "34979151"},
            {"title": "第一章 算好账：战略、业务、财务一本账", "node_id": None},  # 需要获取
            {"title": "第二章 市场预算管理：总目标、分渠道", "node_id": "34544006"},
            {"title": "第三章 市场预算管理：分玩法、分产品", "node_id": "34544007"},
            {"title": "第四章 市场预算管理：分阶段", "node_id": "34544008"},
            {"title": "课程总结", "node_id": "34979152"}
        ]
    },
    {
        "name": "品牌出海私域营销",
        "keyword": "品牌出海私域营销",
        "save_dir": "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/品牌出海私域营销/逐字稿",
        "product_id": None,
        "lessons": []
    }
]

def get_course_outline(product_id):
    """获取课程大纲"""
    url = f"{BASE_API}/b-side/api/web/product/product_id/{product_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': f'https://www.sanjieke.cn/course/detail/sjk/{product_id}'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                product_data = data.get('data', {})
                outline = product_data.get('outlineData', [])
                return outline
    except Exception as e:
        print(f"获取课程大纲失败: {e}")

    return []

def get_lesson_content(product_id, node_id):
    """获取课时内容，包括字幕"""
    url = f"{BASE_API}/b-side/api/web/study/0/{product_id}/content/{node_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': f'https://www.sanjieke.cn/lesson/0/{product_id}/{node_id}'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                nodes = data.get('data', {}).get('nodes', [])
                if nodes:
                    return nodes[0]
    except Exception as e:
        print(f"获取课时内容失败: {e}")

    return None

def get_subtitle_text(subtitle_url):
    """获取字幕文本"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        response = requests.get(subtitle_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"获取字幕文件失败: {e}")

    return None

def parse_vtt_to_text(vtt_content):
    """解析VTT字幕文件为纯文本"""
    lines = vtt_content.split('\n')
    text_parts = []

    for line in lines:
        line = line.strip()
        # 跳过时间戳、空行和WEBVTT头部
        if not line or '-->' in line or line.startswith('WEBVTT') or line.isdigit():
            continue
        # 移除HTML标签
        line = re.sub(r'<[^>]+>', '', line)
        # 移除花括号内容（如样式标签）
        line = re.sub(r'\{[^}]+\}', '', line)
        # 移除时间戳格式的数字
        line = re.sub(r'^\d{2}:\d{2}:\d{2}\.\d+', '', line)
        if line.strip():
            text_parts.append(line.strip())

    return ' '.join(text_parts)

def search_course(keyword):
    """搜索课程"""
    url = f"{BASE_API}/b-side/api/web/search/query"
    params = {
        'keyword': keyword,
        'type': 'course'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                courses = data.get('data', {}).get('list', [])
                return courses
    except Exception as e:
        print(f"搜索课程失败: {e}")

    return []

def save_transcript(save_dir, index, title, content):
    """保存逐字稿到文件"""
    os.makedirs(save_dir, exist_ok=True)

    # 创建文件名
    filename = f"{index:02d}-{title}.md"
    # 清理文件名中的非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filepath = os.path.join(save_dir, filename)

    # 保存内容
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(content)
        f.write("\n")

    return filepath

def download_course(course_info):
    """下载单个课程的所有课时"""
    print(f"\n{'='*60}")
    print(f"开始下载课程: {course_info['name']}")
    print(f"{'='*60}")

    # 如果没有product_id，先搜索
    if not course_info.get('product_id'):
        print("正在搜索课程...")
        courses = search_course(course_info.get('keyword', ''))
        if courses:
            for course in courses:
                if course_info['keyword'] in course.get('name', ''):
                    course_info['product_id'] = str(course['id'])
                    print(f"找到课程ID: {course_info['product_id']}")
                    break
        else:
            print("未找到课程")
            return {"success": 0, "failed": 0, "lessons": []}

    product_id = course_info['product_id']
    save_dir = course_info['save_dir']

    # 获取课程大纲
    print(f"正在获取课程大纲 (ID: {product_id})...")
    outline = get_course_outline(product_id)

    if not outline:
        print("无法获取课程大纲，尝试使用预定义的课时列表...")
        lessons = course_info.get('lessons', [])
    else:
        print(f"获取到 {len(outline)} 个课时")
        lessons = []
        for item in outline:
            lessons.append({
                'title': item.get('name', ''),
                'node_id': str(item.get('node_id', ''))
            })

    # 下载逐字稿
    success_count = 0
    failed_count = 0
    downloaded_lessons = []

    for i, lesson in enumerate(lessons, 1):
        title = lesson.get('title', f'第{i}章')
        node_id = lesson.get('node_id')

        if not node_id:
            print(f"[{i}/{len(lessons)}] 跳过: {title} (无node_id)")
            continue

        print(f"\n[{i}/{len(lessons)}] 正在下载: {title}")
        print(f"  Node ID: {node_id}")

        # 获取课时内容
        content_data = get_lesson_content(product_id, node_id)

        transcript_text = ""

        if content_data:
            # 尝试获取视频字幕
            video_content = content_data.get('videoContent', {})
            subtitles = video_content.get('subtitles', [])

            if subtitles:
                print(f"  找到 {len(subtitles)} 个字幕文件")
                for sub in subtitles:
                    # 优先选择中文字幕
                    if sub.get('language') == 'ZH_CN' or '中文' in sub.get('languageName', ''):
                        subtitle_url = sub.get('url')
                        if subtitle_url:
                            print(f"  正在下载中文字幕...")
                            vtt_content = get_subtitle_text(subtitle_url)
                            if vtt_content:
                                transcript_text = parse_vtt_to_text(vtt_content)
                                break

            # 如果没有字幕，尝试获取文稿内容
            if not transcript_text:
                text_content = content_data.get('textContent', '')
                if text_content:
                    transcript_text = text_content
                    print(f"  使用文稿内容")

        if transcript_text:
            filepath = save_transcript(save_dir, i, title, transcript_text)
            print(f"  ✓ 已保存: {os.path.basename(filepath)}")
            success_count += 1
            downloaded_lessons.append({
                "index": i,
                "title": title,
                "node_id": node_id,
                "filepath": filepath
            })
        else:
            print(f"  ✗ 未能获取内容")
            failed_count += 1
            downloaded_lessons.append({
                "index": i,
                "title": title,
                "node_id": node_id,
                "filepath": None,
                "error": "未能获取内容"
            })

        # 避免请求过快
        time.sleep(1)

    return {
        "success": success_count,
        "failed": failed_count,
        "lessons": downloaded_lessons
    }

def main():
    """主函数"""
    print("三节课课程逐字稿下载工具")
    print("="*60)

    results = []

    for course in COURSES:
        result = download_course(course)
        results.append({
            "course": course['name'],
            "result": result
        })

    # 打印最终统计
    print(f"\n{'='*60}")
    print("下载完成统计")
    print(f"{'='*60}")

    for r in results:
        print(f"\n课程: {r['course']}")
        if 'error' in r['result']:
            print(f"  状态: 失败 - {r['result'].get('error', '未知错误')}")
        else:
            print(f"  成功: {r['result']['success']} 课时")
            print(f"  失败: {r['result']['failed']} 课时")

            if r['result']['lessons']:
                print(f"\n  课时列表:")
                for lesson in r['result']['lessons']:
                    status = "✓" if lesson.get('filepath') else "✗"
                    print(f"    {status} {lesson['index']}. {lesson['title']}")

    print(f"\n{'='*60}")

if __name__ == "__main__":
    main()
