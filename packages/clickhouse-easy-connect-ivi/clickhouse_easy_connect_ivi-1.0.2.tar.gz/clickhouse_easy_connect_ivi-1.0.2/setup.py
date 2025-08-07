from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clickhouse_easy_connect_ivi",
    version="1.0.2",
    author="Your Name",
    author_email="your.email@company.com",
    description="Упрощенная библиотека для работы с ClickHouse",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-company/clickhouse-easy-connect-ivi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
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
    install_requires=[
        "pandas>=1.0.0",
        "clickhouse-connect>=0.5.0",
        "PyYAML>=5.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
        ],
    },
)
