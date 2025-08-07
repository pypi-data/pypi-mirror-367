from setuptools import setup, find_packages

setup(
    name="limipy",
    version="1.0.1",
    author="Anhad Jain",
    author_email="anhad@limiplake.com",
    description="The LimiPlake Python Package- for students AND teachers.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://limiplake.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)