from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mentors-event-hub",
    version="0.1.0",
    author="Mentorstec",
    author_email="diego@mentorstec.com.br",
    description="Event hub for centralized exception logging and monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mentorstec/mentors-event-hub",
    project_urls={
        "Bug Tracker": "https://github.com/mentorstec/mentors-event-hub/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", 
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "azure-servicebus>=7.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    license="MIT",
)