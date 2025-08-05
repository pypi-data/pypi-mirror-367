from setuptools import setup, find_packages

setup(
    name="flashsimplelogger",
    version="0.1.0",
    description="A minimal Python logging wrapper",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Dan Korchunov",
    author_email="dankorchuno89@gmail.com",
    url="https://github.com/dankorchunov89/simplelogger",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license="MIT",
)

