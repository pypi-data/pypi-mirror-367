from setuptools import setup, find_packages

setup(
    name="pyfenix",
    version="0.1.5",
    author="Azeem Teli",
    author_email="tinprogrammers@gmail.com",
    description="A blazing fast and minimal Python full-stack web framework",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tinprogrammers/FeniX",
    license="MIT",
    keywords="python web framework minimal fast cli full-stack fenix",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "rich>=13.0.0"
    ],
    python_requires=">=3.7",
    platforms=["any"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Documentation": "https://github.com/tinprogrammers/FeniX#readme",
        "Source": "https://github.com/tinprogrammers/FeniX",
        "Issue Tracker": "https://github.com/tinprogrammers/FeniX/issues",
        "Changelog": "https://github.com/tinprogrammers/FeniX/releases",
    },
    entry_points={
        "console_scripts": [
            "fx=fenix.cli.main:main",
        ],
    },
)
