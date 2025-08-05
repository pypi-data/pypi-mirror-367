from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quantum-file-system",
    version="0.1.1",
    author="QFS Development Team",
    author_email="cipher_nexus@icloud.com",
    description="A secure web-based file conversion system that encrypts JSON files into QJSON format using custom quantum-inspired encryption algorithms.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Cipher-Prime/quantum-file-system.git",
    packages=find_packages(exclude=["tests*", "examples*"]),
    install_requires=[
        "flask>=3.1.1",
        "werkzeug>=3.1.3",
        "gunicorn>=23.0.0",
    ],
    entry_points={
        "console_scripts": [
            "quantum-fs=qfs.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Filesystems",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    keywords="encryption, quantum, file-system, security, json",
    project_urls={
        "Bug Reports": "https://github.com/Cipher-Prime/quantum-file-system/issues",
        "Source": "https://github.com/Cipher-Prime/quantum-file-system",
        "Documentation": "https://github.com/Cipher-Prime/quantum-file-system#readme",
    },
)