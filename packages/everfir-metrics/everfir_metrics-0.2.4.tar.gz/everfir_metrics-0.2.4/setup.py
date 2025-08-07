from setuptools import setup, find_packages

setup(
    name="everfir_metrics",  # 项目的名称
    version="0.2.4",  # 项目的版本
    description="A simple metrics library for everfir",  # 项目的描述
    long_description=open("README.md").read(),  # 从README文件中读取详细描述
    long_description_content_type="text/markdown",  # 描述文件的格式
    author="houyibin",  # 作者名称
    author_email="houyibin@everfir.com",  # 作者邮箱
    url="https://github.com/everfir/metrics-py",  # 项目的URL
    packages=find_packages(),  # 自动查找项目中的所有包
    install_requires=[
        "requests>=2.25.0",  # requests库的依赖
        "prometheus_client>=0.9.0",  # 添加 prometheus 依赖
        "logger-py>=0.2.3",  # 添加 logger 依赖
        "Flask>=2.0.0",  # 添加 Flask 依赖
        "everfir_logger>=0.0.1",  # 添加 everfir_logger 依赖
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Python版本要求
)
