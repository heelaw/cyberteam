#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Selenium自动下载三节课逐字稿
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import re

# 配置
SEARCH_KEYWORD = "品牌出海DTC电商独立站"
SAVE_DIR = "/Users/cyberrwiz/Desktop/品牌出海数字营销/跨境电商运营力/品牌出海DTC电商独立站/逐字稿"

def setup_driver():
    """设置Chrome浏览器"""
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extract_transcript_from_page(driver):
    """从当前页面提取逐字稿内容"""
    try:
        # 等待页面加载
        time.sleep(3)

        # 尝试点击"文稿"标签
        try:
            transcript_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '文稿') or contains(text(), '字幕') or contains(@class, 'tab') and contains(text(), '文')]"))
            )
            transcript_tab.click()
            time.sleep(2)
        except:
            print("  未找到文稿标签，尝试直接提取内容...")

        # 提取页面中的文本内容
        # 尝试多种选择器
        selectors = [
            "//div[contains(@class, 'transcript') or contains(@class, 'content') or contains(@class, 'text')]",
            "//div[contains(@class, 'lesson-content')]",
            "//div[@class='markdown-body']",
            "//article",
            "//div[contains(text(), '同学你好')]/parent::div",
        ]

        content_elements = []
        for selector in selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    content_elements = elements
                    break
            except:
                continue

        # 提取所有段落
        all_text = []

        # 方法1: 获取所有p标签
        try:
            p_tags = driver.find_elements(By.TAG_NAME, "p")
            for p in p_tags:
                text = p.text.strip()
                if text and len(text) > 5:  # 过滤太短的内容
                    all_text.append(text)
        except:
            pass

        # 方法2: 获取页面主体文本
        if not all_text:
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                all_text = [body.text]
            except:
                pass

        return '\n\n'.join(all_text) if all_text else None

    except Exception as e:
        print(f"  提取内容出错: {e}")
        return None

def save_transcript(save_dir, index, title, content):
    """保存逐字稿到文件"""
    os.makedirs(save_dir, exist_ok=True)

    # 清理标题
    clean_title = re.sub(r'[<>:"/\\|?*]', '_', title)
    filename = f"{index:02d}-{clean_title}.md"
    filepath = os.path.join(save_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(content)
        f.write("\n")

    return filepath

def main():
    print("="*60)
    print("三节课逐字稿自动下载工具")
    print("="*60)
    print(f"\n搜索关键词: {SEARCH_KEYWORD}")
    print(f"保存目录: {SAVE_DIR}\n")

    driver = setup_driver()

    try:
        # 访问三节课首页
        print("正在访问三节课网站...")
        driver.get("https://www.sanjieke.cn")
        time.sleep(3)

        # 检查是否需要登录
        if "login" in driver.current_url.lower():
            print("\n" + "="*60)
            print("需要登录才能访问课程")
            print("="*60)
            print("\n请在浏览器中登录，然后按回车继续...")
            input()

        # 搜索课程
        print(f"\n正在搜索课程: {SEARCH_KEYWORD}")

        # 查找搜索框
        search_inputs = driver.find_elements(By.TAG_NAME, "input")
        search_box = None
        for inp in search_inputs:
            if inp.is_displayed() and inp.is_enabled():
                placeholder = inp.get_attribute('placeholder') or ''
                if '搜索' in placeholder or 'search' in placeholder.lower():
                    search_box = inp
                    break

        if not search_box:
            # 尝试通过类名查找
            search_boxes = driver.find_elements(By.XPATH, "//input[@placeholder='搜索课程' or @placeholder='搜索']")
            if search_boxes:
                search_box = search_boxes[0]

        if search_box:
            search_box.send_keys(SEARCH_KEYWORD)
            time.sleep(1)
            search_box.submit()
            time.sleep(3)
            print("搜索完成")
        else:
            print("未找到搜索框，尝试直接访问课程页面...")
            # 这里可以添加直接访问课程URL的逻辑
            print("\n请提供课程的具体URL，或者手动搜索后复制课程URL")
            print("然后按回车继续...")
            input()

        # 查找并点击课程
        print("\n正在查找目标课程...")
        course_links = driver.find_elements(By.TAG_NAME, "a")
        target_link = None

        for link in course_links:
            text = link.text or ''
            href = link.get_attribute('href') or ''
            if SEARCH_KEYWORD in text or (href and 'course' in href):
                print(f"找到可能的课程链接: {text[:50]}")
                target_link = link
                break

        if target_link:
            target_link.click()
            time.sleep(3)
            print("已进入课程页面")
        else:
            print("\n未自动找到课程链接")
            print("请手动点击课程，然后按回车继续...")
            input()

        # 获取课程大纲
        print("\n正在获取课程大纲...")
        lesson_links = []

        # 查找章节链接
        outline_items = driver.find_elements(By.XPATH, "//li[contains(@class, 'outline') or contains(@class, 'chapter') or contains(@class, 'lesson')]")

        for item in outline_items:
            try:
                link = item.find_element(By.TAG_NAME, "a")
                title = link.text.strip()
                if title:
                    lesson_links.append({
                        'title': title,
                        'element': link
                    })
            except:
                pass

        if not lesson_links:
            # 尝试其他选择器
            lesson_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'lesson')]")

        print(f"找到 {len(lesson_links)} 个课时")

        # 逐个提取逐字稿
        downloaded = []

        for i, lesson in enumerate(lesson_links, 1):
            title = lesson.get('title', f'第{i}章')
            print(f"\n[{i}/{len(lesson_links)}] 正在处理: {title}")

            # 点击章节
            if 'element' in lesson:
                lesson['element'].click()
            else:
                driver.get(lesson.get('url', ''))

            time.sleep(3)

            # 提取逐字稿
            content = extract_transcript_from_page(driver)

            if content:
                filepath = save_transcript(SAVE_DIR, i, title, content)
                print(f"  ✓ 已保存: {os.path.basename(filepath)}")
                downloaded.append({
                    'index': i,
                    'title': title,
                    'filepath': filepath
                })
            else:
                print(f"  ✗ 未能提取内容")
                downloaded.append({
                    'index': i,
                    'title': title,
                    'filepath': None
                })

            # 等待避免请求过快
            time.sleep(2)

        # 打印结果
        print(f"\n{'='*60}")
        print("下载完成!")
        print(f"{'='*60}")
        print(f"总计: {len(downloaded)} 个课时")
        print(f"成功: {sum(1 for d in downloaded if d['filepath'])} 个")
        print(f"失败: {sum(1 for d in downloaded if not d['filepath'])} 个")
        print(f"\n保存目录: {SAVE_DIR}\n")

        print("文件列表:")
        for d in downloaded:
            status = "✓" if d['filepath'] else "✗"
            print(f"  {status} {d['index']}. {d['title']}")

        # 等待用户查看结果
        print("\n按回车键退出...")
        input()

    except Exception as e:
        print(f"\n程序出错: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
