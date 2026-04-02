#!/usr/bin/env python3
import requests
import json

# 尝试获取"如何拉高营销ROI"的课程列表
# 从现有文件中我们知道project_id是34002386

def get_course_lessons(project_id):
    """获取课程的所有课时"""
    # 尝试通过API获取
    api_url = "https://www.sanjieke.cn/api/lesson/list"
    params = {
        "project_id": project_id
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://www.sanjieke.cn/"
    }
    
    try:
        response = requests.get(api_url, params=params, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
    except Exception as e:
        print(f"Error: {e}")
    
    return None

# 尝试获取课程
get_course_lessons("34002386")
