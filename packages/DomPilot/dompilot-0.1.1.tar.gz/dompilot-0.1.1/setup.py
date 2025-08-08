from setuptools import setup, find_packages

setup(
    name="DomPilot",
    version="0.1.1",
    description="AI webscraping library powered by Playwright and LLMs",
    author="TheNoobiCat",
    author_email="",
    url="https://github.com/TheNoobiCat/DomPilot",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "playwright>=1.40.0",
        "playwright-stealth",
        "httpx",
        "jsonschema",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
