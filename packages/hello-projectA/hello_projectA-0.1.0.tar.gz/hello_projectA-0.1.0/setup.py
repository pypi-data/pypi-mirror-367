from setuptools import setup, find_packages

setup(
    name="hello_projectA",  # 包名称
    version="0.1.0",    # 版本号
    author="sz",
    author_email="usaq1@163.com",
    description="a test",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sunzhong0201/my_project",
    packages=find_packages(),  # 自动发现所有包
    install_requires=[
        # 列出依赖项，如：
        # "requests>=2.25.1",
        # "numpy>=1.20.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Python版本要求
)