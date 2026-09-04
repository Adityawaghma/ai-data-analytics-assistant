from setuptools import setup, find_packages

setup(
    name="ai-data-analytics-assistant",
    version="1.0.0",
    author="Adityawaghma",
    description="AI-powered desktop analytics app",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=open("requirements.txt").read().splitlines(),
    python_requires=">=3.10",
)
