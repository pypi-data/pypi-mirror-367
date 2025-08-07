from setuptools import setup, find_packages

setup(
    name="qjacklogo",
    version="0.2.2",
    packages=find_packages(),
    install_requires=[
        "pyfiglet",
        "colorama"
    ],
    author="jamalnggau",
    description="Animated terminal logo with Arabic text and rainbow effect.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "qjacklogo=qjacklogo.logo:start_animations"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
