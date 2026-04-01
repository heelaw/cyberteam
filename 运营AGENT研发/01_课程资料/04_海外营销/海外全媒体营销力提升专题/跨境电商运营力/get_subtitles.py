#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取课程字幕API脚本
"""

import requests
import json
import os
import re

# 课程配置
COURSES = {
    "B2B出海营销LinkedIn": {
        "course_id": "34001658",
        "chapters": [
            {"node_id": "34298522", "title": "一、B2B企业出海营销策略及方法", "subtitle_id": "14539"},
            {"node_id": "34298523", "title": "二、LinkedIn领英职场社交平台为何值得投入？", "subtitle_id": "14540"},
            {"node_id": "34298524", "title": "三、如何在LinkedIn进行内容营销，与高质量人群沟通？", "subtitle_id": "14541"},
            {"node_id": "34298525", "title": "四、如何在LinkedIn领英进行广告投放，有效提升收益？", "subtitle_id": "14542"},
            {"node_id": "34298526", "title": "课程总结", "subtitle_id": "14543"}
        ],
        "save_dir": "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/B2B出海营销LinkedIn/逐字稿"
    }
}

def get_subtitle_text(course_id, node_id, subtitle_id):
    """获取字幕文本"""
    # 首先获取内容API以获取正确的subtitle ID
    content_url = f"https://web-api.sanjieke.cn/b-side/api/web/study/0/{course_id}/content/{node_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json'
    }

    try:
        resp = requests.get(content_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('code') == 200:
                nodes = data.get('data', {}).get('nodes', [])
                if nodes:
                    video_content = nodes[0].get('videoContent', {})
                    subtitles = video_content.get('subtitles', [])

                    # 查找中文字幕
                    for sub in subtitles:
                        if sub.get('language') == 'ZH_CN' or '中文' in sub.get('languageName', ''):
                            subtitle_url = sub.get('url')
                            if subtitle_url:
                                # 请求VTT文件
                                vtt_resp = requests.get(subtitle_url, headers=headers, timeout=10)
                                if vtt_resp.status_code == 200:
                                    return parse_vtt(vtt_resp.text)
    except Exception as e:
        print(f"获取字幕出错: {e}")

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
                    # 清理时间戳和其他标记
                    text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d+', '', text)
                    text = re.sub(r'<[^>]+>', '', text)
                    text = re.sub(r'\{[^}]+\}', '', text)
                    text = text.strip()
                    if text and len(text) > 1:
                        subtitles.append(text)
                current_text = []
        elif '-->' not in line and not line.startswith('WEBVTT') and not line.startswith('NOTE'):
            # 清理字幕文本
            text = re.sub(r'<[^>]+>', '', line)
            text = re.sub(r'\{[^}]+\}', '', text)
            if text and text.strip():
                current_text.append(text.strip())

    return subtitles

def save_subtitle(chapter_index, title, subtitles, save_dir):
    """保存字幕到文件"""
    os.makedirs(save_dir, exist_ok=True)

    filename = f"{chapter_index}-{title}.md"
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filepath = os.path.join(save_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        for line in subtitles:
            f.write(line + '\n')

    print(f"已保存: {filepath} ({len(subtitles)} 行)")

def main():
    """主函数"""
    for course_name, course_info in COURSES.items():
        print(f"\n处理课程: {course_name}")
        print(f"课程ID: {course_info['course_id']}")

        for i, chapter in enumerate(course_info['chapters']):
            node_id = chapter['node_id']
            title = chapter['title']

            print(f"正在处理第 {i+1} 章: {title}")

            subtitles = get_subtitle_text(course_info['course_id'], node_id, chapter.get('subtitle_id'))

            if subtitles:
                save_subtitle(i + 1, title, subtitles, course_info['save_dir'])
            else:
                print(f"无法获取第 {i+1} 章的字幕")

if __name__ == "__main__":
    main()
