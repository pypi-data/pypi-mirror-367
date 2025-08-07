from setuptools import setup, find_packages

setup(
    name="mcp_md2xmind",  # 包名，pip install 时用这个
    version="0.1.0",
    description="markdown to xmind tool",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="mengyu",
    author_email="pengmengyu97@gmail.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
