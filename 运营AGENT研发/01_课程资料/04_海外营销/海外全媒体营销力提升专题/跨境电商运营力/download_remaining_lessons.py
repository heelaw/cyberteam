#!/usr/bin/env python3
import requests
import json
import time
import os
import re
from pathlib import Path

# 已知课程信息
courses = {
    "如何拉高营销ROI": {
        "project_id": "34002386",
        "save_dir": "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/如何拉高营销ROI/逐字稿",
        # 已下载的文件
        "downloaded": ["00-课程导读.md", "01-第一章-算好账战略业务财务一本账.md"]
    },
    "品牌出海私域营销": {
        "save_dir": "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/品牌出海私域营销/逐字稿",
        "downloaded": []
    }
}

def get_course_outline(project_id):
    """获取课程大纲"""
    # 尝试从课程内容API获取
    api_url = f"https://web-api.sanjieke.cn/b-side/api/web/study/0/{project_id}/index"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": f"https://www.sanjieke.cn/lesson/0/{project_id}"
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"API Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
            return data
    except Exception as e:
        print(f"Error getting outline: {e}")
    return None

# 尝试获取课程大纲
print("尝试获取课程大纲...")
outline = get_course_outline("34002386")
