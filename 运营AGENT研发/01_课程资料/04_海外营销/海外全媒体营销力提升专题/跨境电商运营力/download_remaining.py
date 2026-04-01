#!/usr/bin/env python3
"""
下载剩余的课程逐字稿
"""
import requests
import json
import time
import os
from pathlib import Path

# 课程ID映射
courses = {
    "如何拉高营销ROI": {
        "project_id": "34002386",
        "lessons": [
            "34544004",  # 第一章 算好账
            # 需要获取更多lesson ID
        ]
    },
    "品牌出海私域营销": {
        "project_id": "需要获取",
        "lessons": []
    }
}

# Session headers
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

def get_lesson_content(lesson_id):
    """获取课程内容"""
    url = f"https://www.sanjieke.cn/lesson/0/34002386/{lesson_id}"
    print(f"正在访问: {url}")
    return requests.get(url, headers=headers)

# 先尝试获取课程列表
print("尝试获取课程列表...")
