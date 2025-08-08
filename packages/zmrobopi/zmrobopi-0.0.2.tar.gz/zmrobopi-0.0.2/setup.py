from setuptools import setup, find_packages

setup(
    name="zmrobopi",
    version="0.0.2",
    author="kimbell",
    author_email="you@example.com",
    description="控制QML Canvas绘图的库",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/",  # 可留空或写私有地址
    packages=["zmrobopi"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
)
