from setuptools import setup, find_packages

setup(
    name="pynotiq_client",
    version="0.4.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0"
    ],
    description="Python client library for adding messages to PyNotiQ queue with local and remote support",
    author="Your Name",
    url="https://github.com/downlevel/pynotiq_client",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)