from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="QuickMediaDL",
    version="0.2.0",
    author="Amirhossein bahrami",
    author_email="amirbaahrami@gmail.com",
    description="An advanced library for downloading video and audio from online sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Amirprx3/QuickMediaDL",
    packages=find_packages(),
    install_requires=[
        "yt-dlp",
        "tqdm",
        "ffmpeg-python"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Video :: Conversion", 
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.7',
    keywords="downloader video audio youtube yt-dlp",
)