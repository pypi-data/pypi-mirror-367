# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="chinaunicom-agent",
    version="0.3.5",
    author="zhaoyongzheng",
    author_email="17668860550@163.com",
    description="可为山东联通产互员工自动填报工时，整理周报",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/your-package",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx",
        "pendulum",
        "pymsgbox",
        "pywinauto",
        "selenium",
        "pytesseract",
        "Pillow",
        "ddddocr",
        "requests",
        "pyautogui",
        "pyperclip",
        "opencv-python",
        "typing-extensions",
        "mcp",
    ],
)