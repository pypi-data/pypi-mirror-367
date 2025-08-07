from setuptools import setup, find_packages

setup(
    name="axiomelectrus",
    version="1.1.1",
    author="Pawan Kumar",
    author_email="aegis.invincible@gmail.com",
    description="Electrus is a lightweight asynchronous & synchronous database module designed for Python.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/axiomchronicles/electrus",
    packages=find_packages(include=["axiomelectrus", "axiomelectrus.*"]),  # ✅ include subpackages!
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "database", "json", "nosql", "lightweight", "async", "synchronous", "electrus", "mongodb", "python-database"
    ],
    python_requires=">=3.6",
    license="MIT",
)
