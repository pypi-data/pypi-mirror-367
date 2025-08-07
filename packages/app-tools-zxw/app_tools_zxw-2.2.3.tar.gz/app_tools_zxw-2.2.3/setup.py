from setuptools import setup, find_packages

setup(
    name="app_tools_zxw",
    version="2.2.3",
    packages=find_packages(),
    install_requires=[
        'pycryptodome>=3.20.0,<=3.22.0',
        'fastapi>=0.112.0,<0.113',
        'jose>=1.0.0,<1.1.0',
        "aiohttp>=3.12.14",  # 'aiohttp>=3.10.5,<3.11.0'
        'httpx>=0.28.1',  # 0.23.3,<=0.27.0
        'qrcode>=7.4.2,<7.5.0',
        "cryptography==44.0.1",  # cryptography>=43.0.0,<44.0.0
        'alipay-zxw==0.0.4',
        'aiofiles==24.1.0',
        'app-store-server-library[async]==1.9.0'
    ],
    author="薛伟的小工具",
    author_email="",
    description="app开发相关的各种sdk",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sunshineinwater/",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
