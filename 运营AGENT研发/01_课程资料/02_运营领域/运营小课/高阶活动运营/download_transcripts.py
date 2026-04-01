#!/usr/bin/env python3
"""
三节课课程逐字稿下载脚本
用于批量下载课程的文稿内容
"""

import requests
import json
import time
import os
import re
from urllib.parse import urljoin

# 配置信息
COURSE_URL = "https://www.sanjieke.cn/course/detail/sjk/8000079"
SAVE_PATH = "/Users/cyberrwiz/Desktop/黄有璨系列课程/高阶活动运营/逐字稿"
PHONE = "13434216813"
PASSWORD = "Aa12345678"

# Session会话
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.sanjieke.cn/'
})

def login():
    """登录三节课"""
    print("正在登录三节课...")

    # 首先获取登录页面
    login_url = "https://passport.sanjieke.cn/account"
    try:
        response = session.get(login_url, timeout=15)
        print(f"获取登录页面状态: {response.status_code}")
    except Exception as e:
        print(f"获取登录页面失败: {e}")
        return False

    # 登录API
    login_api = "https://passport.sanjieke.cn/api/login"
    login_data = {
        'phone': PHONE,
        'password': PASSWORD,
        'captcha': ''
    }

    try:
        response = session.post(login_api, json=login_data, timeout=15)
        print(f"登录API状态: {response.status_code}")
        result = response.json()

        if result.get('code') == 0 or result.get('ret') == 0:
            print("登录成功！")
            return True
        else:
            print(f"登录失败: {result}")
            return False
    except Exception as e:
        print(f"登录请求失败: {e}")
        return False

def get_course_data():
    """获取课程数据"""
    print("正在获取课程数据...")

    try:
        response = session.get(COURSE_URL, timeout=15)
        print(f"课程页面状态: {response.status_code}")

        # 提取__NUXT__数据
        match = re.search(r'<script>window\.__NUXT__\s*=\s*(.+?)</script>', response.text)
        if not match:
            print("未找到课程数据")
            return None

        # 清理数据
        nuxt_data = match.group(1)

        # 这个数据是一个立即执行的函数，需要手动解析
        # 让我们尝试用正则提取关键信息
        return extract_course_outline(nuxt_data)

    except Exception as e:
        print(f"获取课程数据失败: {e}")
        return None

def extract_course_outline(nuxt_data):
    """从NUXT数据中提取课程大纲"""
    lessons = []

    # 使用正则提取课程信息
    # 查找所有的 node_id 和 name
    node_pattern = r'node_id:(\d+),name:"([^"]+)",type:(\d+),final_content_type:(\d+)'

    matches = re.findall(node_pattern, nuxt_data)

    for match in matches:
        node_id, name, type_val, content_type = match
        lessons.append({
            'node_id': node_id,
            'name': name,
            'type': type_val,
            'content_type': content_type
        })

    return lessons

def get_lesson_transcript(node_id):
    """获取课时文稿"""
    # 文稿API URL（需要根据实际情况调整）
    transcript_url = f"https://www.sanjieke.cn/api/course/lesson/{node_id}/transcript"

    try:
        response = session.get(transcript_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('content', '')
        return None
    except Exception as e:
        print(f"获取文稿失败 (node_id: {node_id}): {e}")
        return None

def sanitize_filename(filename):
    """清理文件名"""
    # 移除或替换不合法的字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.strip()
    return filename

def save_transcript(index, title, content):
    """保存文稿到文件"""
    if not content:
        return False

    filename = f"{index:02d}-{sanitize_filename(title)}.md"
    filepath = os.path.join(SAVE_PATH, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(content)
        print(f"已保存: {filename}")
        return True
    except Exception as e:
        print(f"保存文件失败 ({filename}): {e}")
        return False

def main():
    """主函数"""
    # 创建保存目录
    os.makedirs(SAVE_PATH, exist_ok=True)

    # 登录
    if not login():
        print("登录失败，无法继续")
        return

    time.sleep(1)

    # 获取课程数据
    lessons = get_course_data()
    if not lessons:
        print("获取课程数据失败")
        return

    print(f"\n共找到 {len(lessons)} 个课时\n")

    # 遍历每个课时
    success_count = 0
    no_transcript = []

    for idx, lesson in enumerate(lessons, 1):
        print(f"\n[{idx}/{len(lessons)}] 正在处理: {lesson['name']}")

        # 获取文稿
        transcript = get_lesson_transcript(lesson['node_id'])

        if transcript:
            # 保存文稿
            if save_transcript(idx, lesson['name'], transcript):
                success_count += 1
        else:
            print(f"  -> 该课时没有文稿")
            no_transcript.append(lesson['name'])

        # 避免请求过快
        time.sleep(0.5)

    # 打印汇总
    print(f"\n\n{'='*50}")
    print(f"下载完成！")
    print(f"成功下载: {success_count} 个")
    print(f"没有文稿: {len(no_transcript)} 个")

    if no_transcript:
        print(f"\n以下课时没有文稿:")
        for title in no_transcript:
            print(f"  - {title}")

if __name__ == "__main__":
    main()
