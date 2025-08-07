from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="linaix",
    version="0.1.1",
    author="Adir Ali Yerima",
    description="A Linux terminal interface with natural language processing capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AdirAli/linaix",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "linaix=linaix.linaix:main",
        ],
    },
    include_package_data=True,
    package_data={
        "linaix": ["*.txt", "*.md", "*.png", "*.gif"],
    },
) 