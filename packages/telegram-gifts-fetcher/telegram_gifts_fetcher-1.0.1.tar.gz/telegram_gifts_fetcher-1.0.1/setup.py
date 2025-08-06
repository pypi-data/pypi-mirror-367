from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="telegram-gifts-fetcher",
    version="1.0.1",
    author="Th3ryks",
    author_email="",
    description="The first and only library to fetch Telegram Star Gifts from user profiles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Th3ryks/telegram-gifts-fetcher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "telethon>=1.40.0",
        "loguru>=0.6.0",
        "python-dotenv>=0.19.0",
    ],
    keywords="telegram, gifts, star gifts, api, telethon",
    project_urls={
        "Bug Reports": "https://github.com/Th3ryks/telegram-gifts-fetcher/issues",
        "Source": "https://github.com/Th3ryks/telegram-gifts-fetcher",
    },
)