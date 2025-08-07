# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="chinaunicom-agent",
    version="0.3.2",
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
        "httpx>=0.24.1",
        "pendulum>=2.1.2",
        "pymsgbox>=1.0.9",
        "pywinauto>=0.6.8",
        "selenium>=4.10.0",
        "pytesseract>=0.3.10",
        "Pillow>=9.5.0",
        "ddddocr>=1.4.7",
        "requests>=2.31.0",
        "pyautogui>=0.9.53",
        "pyperclip>=1.8.2",
        "opencv-python>=4.7.0.72",
        "pywin32>=306; platform_system=='Windows'",
        "typing-extensions>=4.7.1"
    ],
)