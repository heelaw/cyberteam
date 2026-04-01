#!/usr/bin/env python3
"""
三节课课程逐字稿下载脚本（使用Selenium）
需要安装: pip3 install selenium webdriver-manager
"""

import time
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 配置信息
COURSE_URL = "https://www.sanjieke.cn/course/detail/sjk/8000079"
SAVE_PATH = "/Users/cyberrwiz/Desktop/黄有璨系列课程/高阶活动运营/逐字稿"
PHONE = "13434216813"
PASSWORD = "Aa12345678"

# 课程课时列表（按顺序）
LESSONS = [
    {"node_id": "18689084", "title": "01-从根本上理解活动运营"},
    {"node_id": "18690581", "title": "02-常见的活动形式和用户吸引逻辑"},
    {"node_id": "18690589", "title": "03-如何梳理活动的核心流程"},
    {"node_id": "18690605", "title": "04-如何对一个活动进行微创新"},
    {"node_id": "18690615", "title": "05-活动页面的价值和设计原则"},
    {"node_id": "18690650", "title": "06-如何借鉴自如薅羊毛活动"},
    {"node_id": "18690625", "title": "07-如何借鉴简书神转折大赛"},
    {"node_id": "18690689", "title": "08-策划一个完整活动的6大基本要素"},
    {"node_id": "18690701", "title": "09-如何结合目标设计活动后端策略"},
    {"node_id": "18690705", "title": "10-活动主题策划及前端玩法设计"},
    {"node_id": "18690712", "title": "11-活动风险评估"},
    {"node_id": "18690721", "title": "12-活动的执行与落地四步走"},
    {"node_id": "18690728", "title": "13-课程知识要点总结"},
    {"node_id": "18690760", "title": "14-如何利用活动中台做活动"},
]

def init_driver():
    """初始化Chrome驱动"""
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # 如果需要无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def login(driver):
    """登录三节课"""
    print("正在登录三节课...")

    try:
        # 访问登录页面
        driver.get("https://passport.sanjieke.cn/account")

        # 等待页面加载
        wait = WebDriverWait(driver, 10)

        # 输入手机号
        phone_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='手机']"))
        )
        phone_input.clear()
        phone_input.send_keys(PHONE)

        # 输入密码
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.clear()
        password_input.send_keys(PASSWORD)

        # 点击登录按钮
        login_button = driver.find_element(By.CSS_SELECTOR, "button[class*='login']")
        login_button.click()

        # 等待登录完成
        time.sleep(3)

        # 检查是否登录成功
        if "sanjieke" in driver.current_url.lower():
            print("登录成功！")
            return True
        else:
            print("登录可能失败，请检查...")
            return False

    except Exception as e:
        print(f"登录过程出错: {e}")
        return False

def get_transcript(driver, node_id, title):
    """获取课时文稿"""
    print(f"正在获取: {title} (node_id: {node_id})")

    try:
        # 访问课时页面
        lesson_url = f"https://www.sanjieke.cn/lesson/{node_id}"
        driver.get(lesson_url)

        # 等待页面加载
        wait = WebDriverWait(driver, 15)
        time.sleep(2)

        # 查找并点击"文稿"标签
        try:
            transcript_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), '文稿') or contains(text(), '逐字稿')]"))
            )
            transcript_tab.click()
            time.sleep(1)
        except:
            print("  -> 未找到文稿标签，可能该课时没有文稿")

        # 获取文稿内容
        try:
            # 尝试多种可能的定位方式
            content_selectors = [
                "//div[contains(@class, 'manuscript') or contains(@class, 'transcript') or contains(@class, 'content')]",
                "//div[@class='lesson-manuscript']",
                "//div[@class='transcript-content']",
            ]

            content = None
            for selector in content_selectors:
                try:
                    content_element = driver.find_element(By.XPATH, selector)
                    content = content_element.text
                    if content and len(content) > 10:
                        break
                except:
                    continue

            if content:
                return content
            else:
                # 尝试从页面源码中提取
                page_source = driver.page_source
                # 查找包含文稿内容的script标签
                match = re.search(r'"manuscript"|"transcript"|"content"\s*:\s*"([^"]+)"', page_source)
                if match:
                    return match.group(1)

                print("  -> 未能提取到文稿内容")
                return None

        except Exception as e:
            print(f"  -> 获取文稿内容失败: {e}")
            return None

    except Exception as e:
        print(f"  -> 访问课时页面失败: {e}")
        return None

def save_transcript(title, content):
    """保存文稿到文件"""
    if not content:
        return False

    filename = f"{title}.md"
    filepath = os.path.join(SAVE_PATH, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(content)
        print(f"  ✓ 已保存: {filename}")
        return True
    except Exception as e:
        print(f"  ✗ 保存文件失败: {e}")
        return False

def main():
    """主函数"""
    # 创建保存目录
    os.makedirs(SAVE_PATH, exist_ok=True)

    # 初始化驱动
    print("正在初始化浏览器...")
    driver = init_driver()

    try:
        # 登录
        if not login(driver):
            print("登录失败，无法继续")
            return

        # 下载逐字稿
        print(f"\n开始下载逐字稿，共 {len(LESSONS)} 个课时\n")

        success_count = 0
        no_transcript = []

        for idx, lesson in enumerate(LESSONS, 1):
            print(f"\n[{idx}/{len(LESSONS)}] {lesson['title']}")

            # 获取文稿
            content = get_transcript(driver, lesson['node_id'], lesson['title'])

            if content:
                # 保存文稿
                if save_transcript(lesson['title'], content):
                    success_count += 1
            else:
                no_transcript.append(lesson['title'])

            # 避免请求过快
            time.sleep(1)

        # 打印汇总
        print(f"\n\n{'='*50}")
        print(f"下载完成！")
        print(f"成功下载: {success_count} 个")
        print(f"没有文稿: {len(no_transcript)} 个")

        if no_transcript:
            print(f"\n以下课时没有文稿:")
            for title in no_transcript:
                print(f"  - {title}")

    finally:
        # 关闭浏览器
        print("\n按Enter键关闭浏览器...")
        input()
        driver.quit()

if __name__ == "__main__":
    main()
