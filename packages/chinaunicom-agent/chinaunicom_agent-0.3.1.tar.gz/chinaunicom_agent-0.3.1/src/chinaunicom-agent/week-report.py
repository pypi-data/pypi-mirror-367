from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import time
from pendulum import today
from pymsgbox import password
from pywinauto.findwindows import find_element
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pytesseract
from PIL import Image
import ddddocr
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime, timedelta
import requests
from pywinauto.application import Application
import time
import subprocess
import pyautogui
import os
import pyperclip
from selenium.webdriver.chrome.options import Options
import mcp

# 个人配置项：
# 用户名配置
username = os.environ.get('CHINAUNICOM_USERNAME')
# 密码配置
password = os.environ.get('CHINAUNICOM_PASSWORD')
# iNode安装地址配置
inode_location = os.environ.get('INODELOCATION')
# 周报时间
# today = datetime.now()-timedelta(days=7)
today = datetime.now()

# 初始化 FastMCP server
mcp = FastMCP("week-report")

def scan_code(driver):
    try:
        # 使用OCR识别输入验证码-ddddocr
        time.sleep(1)
        captcha_element = driver.find_element(By.XPATH,
                                            "/html/body/div/div/div[2]/div[2]/div[2]/div/form/div[3]/div/div/span/div/div[2]/a/img")
        captcha_element.screenshot("captcha.png")
        ocr = ddddocr.DdddOcr()
        with open("captcha.png", 'rb') as f:
            image_bytes = f.read()
        captcha = ocr.classification(image_bytes)
        print("识别的验证码为：" + captcha)
        driver.find_element(By.ID, "captcha").send_keys(captcha)
        time.sleep(3)

        # 点击登录按钮
        submit_button = driver.find_element(By.CLASS_NAME, "ant-btn")
        submit_button.click()
    except Exception as e:
        scan_code(driver)

@mcp.tool()
async def weekday_log(weekday:str, work_hour:float, work_content:str) -> str:
    """记录工作日志
    Args:
        weekday: 工作日期，格式：xxxx年x月x日  月和日前面不要加0
        work_hour: 工作时长
        work_content: 工作内容
    """
    # username = input("请输入项目过程管理平台用户名：")
    # password = input("请输入项目过程管理平台密码：")

    print("weekday_log begin")
    # 添加无头模式选项
    chrome_options = Options()
    # chrome_options.add_argument('--headless')

    # 初始化浏览器
    driver = webdriver.Chrome(options=chrome_options)

    # 打开网页-origin
    driver.get("http://192.168.24.37:8080/udpm/#/login")

    # 登录页输入用户名
    search_box = driver.find_element(By.ID, "username")
    search_box.send_keys(username)

    # 登录页输入密码
    search_box = driver.find_element(By.ID, "password")
    search_box.send_keys(password)

    # 使用OCR识别输入验证码-ddddocr
    scan_code(driver)
    time.sleep(5)

    # 关闭通知按钮
    tip_button = driver.find_elements(By.CLASS_NAME, "ant-btn-primary")[1]
    tip_button.click()

    td_btn = driver.find_element(By.XPATH, f"//td[@title='{weekday}']")
    td_btn.click()
    time.sleep(2)

    driver.find_elements(By.CLASS_NAME, "ant-table-tbody")[1].find_elements(By.TAG_NAME, "tr")[0].find_elements(By.TAG_NAME, "td")[3].find_element(By.TAG_NAME, "input").send_keys(str(work_hour))
    driver.find_elements(By.CLASS_NAME, "ant-table-tbody")[1].find_elements(By.TAG_NAME, "tr")[0].find_elements(By.TAG_NAME, "td")[5].find_element(By.TAG_NAME, "textarea").send_keys(work_content)
    time.sleep(2)

    # 取消
    # close_btn = driver.find_elements(By.CSS_SELECTOR, ".ant-modal-footer")[1].find_element(By.CSS_SELECTOR, ".ant-btn-default")
    # 确定
    close_btn = driver.find_elements(By.CSS_SELECTOR, ".ant-modal-footer")[1].find_element(By.CSS_SELECTOR, ".ant-btn-primary")
    close_btn.click()

    return "成功"



@mcp.tool()
async def week_report() -> str:
    """获取周报内容
    """
    # username = input("请输入项目过程管理平台用户名：")
    # password = input("请输入项目过程管理平台密码：")

    # 添加无头模式选项
    chrome_options = Options()
    # chrome_options.add_argument('--headless')

    # 初始化浏览器
    driver = webdriver.Chrome(options=chrome_options)

    # 打开网页-origin
    driver.get("http://192.168.24.37:8080/udpm/#/login")

    # 登录页输入用户名
    search_box = driver.find_element(By.ID, "username")
    search_box.send_keys(username)

    # 登录页输入密码
    search_box = driver.find_element(By.ID, "password")
    search_box.send_keys(password)

    # 使用OCR识别输入验证码-ddddocr
    scan_code(driver)
    time.sleep(5)

    # 关闭通知按钮
    tip_button = driver.find_elements(By.CLASS_NAME, "ant-btn-primary")[1]
    tip_button.click()

    # 获取今天的日期
    monday = today - timedelta(days=today.weekday())
    weekdays = []
    for i in range(5):  # 0到4代表周一到周五
        day = monday + timedelta(days=i)
        format_date = f"{day.year}年{day.month}月{day.day}日"
        weekdays.append(format_date)
    print("weekdays:" + str(weekdays))

    day_work_list = []
    lack_flag = True

    for index, weekday in enumerate(weekdays):
        td_btn = driver.find_element(By.XPATH, f"//td[@title='{weekday}']")
        td_btn.click()
        time.sleep(2)
        # day_work = driver.find_element(By.XPATH, "/html/body/div[6]/div/div[2]/div/div[2]/div[2]/div/div/div/div/div/div/div/div/div/table/tbody/tr/td[6]/div/span").text
        try:
            day_work = \
            driver.find_elements(By.CLASS_NAME, "ant-table-tbody")[1].find_elements(By.TAG_NAME, "td")[
                -2].find_element(By.TAG_NAME, "span").text
        except Exception as e:
            if lack_flag:
                continue
            else:
                break

        day_work_list.append("星期" + str(index + 1) + ":" + day_work)
        print("day_work:" + str(day_work))
        lack_flag = False
        close_btn = driver.find_element(By.CSS_SELECTOR, "svg[data-icon='close']")
        close_btn.click()
    return "\n---\n".join(day_work_list)

if __name__ == "__main__":
    mcp.run(transport='stdio')