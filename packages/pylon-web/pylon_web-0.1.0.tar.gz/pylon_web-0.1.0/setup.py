from setuptools import setup, find_packages

setup(
    name="pylon-web",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["httptools>=0.5.0"],
    author="LONGTIME",
    author_email="noreply@long-time.ru",
    description="A blazing fast Python web server library",
    classifiers=[
        "Programming Language :: Python :: 3.8+",
        "License :: OSI Approved :: MIT License",
    ],
)