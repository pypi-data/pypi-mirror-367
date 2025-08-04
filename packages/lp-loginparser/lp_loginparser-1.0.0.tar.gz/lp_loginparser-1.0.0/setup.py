from setuptools import setup, find_packages

setup(
    name="lp-loginparser",
    version="1.0.0",
    description="Login Form Extractor and Parser with Basic Auth Automation",
    author="[Ph4nt01]",
    author_email="ph4nt0.84@gmail.com",
    url="https://github.com/Ph4nt01/LP-LoginParser",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "requests",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "lp-loginparser=lp_loginparser.cli:cli_main"
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Security",
        "Intended Audience :: Developers",
    ]
)
