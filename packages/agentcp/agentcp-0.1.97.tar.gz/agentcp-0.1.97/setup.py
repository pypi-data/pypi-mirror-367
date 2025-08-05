from setuptools import setup, find_packages
from pathlib import Path

# 使用 Path 确保跨平台兼容性，并显式处理编码
long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="agentcp",
    version="0.1.97",
    description=(
        "ACP是一个开放协议，用于解决Agent互相通信协作的问题。"
        "ACP定义了agent的数据规范、通信及授权规范。\n\n"
        "AgentCP Python SDK是一个基于ACP协议的Agent标准通信库，"
        "支持Agent间的身份认证、通信、多Agent协作、异步消息处理、内网穿透和负载均衡。"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="liwenjiang",
    author_email="19169495461@163.com",
    url="https://github.com/auliwenjiang/agentcp",
    packages=find_packages(where="."),
    package_dir={"": "."},
    include_package_data=True,
    install_requires=[
        "cryptography>=3.4.7",
        "requests>=2.26.0",
        "websocket-client>=1.2.1",
        "python-dotenv>=0.19.0",
        "typing-extensions>=4.0.1",
        "openai>=1.68.2",
        "flask>=3.0.1",
        "flask[async]>=1.0.1",  # 注意：flask[async] 是 Flask 的扩展依赖，需确保写法正确
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
    keywords="Agent Communication Protocol",
    project_urls={
        "Bug Reports": "https://github.com/auliwenjiang/agentcp/issues",
        "Source": "https://github.com/auliwenjiang/agentcp",
    },
)