from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rtx50-compat",
    version="1.0.0",
    author="JW",
    author_email="jw@diablogato.com",
    description="RTX 50-series GPU compatibility layer for PyTorch and CUDA - enables sm_120 support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jw/rtx50-compat",
    py_modules=["rtx50_compat"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Don't require torch as dependency - user should have it installed
    ],
    extras_require={
        "dev": ["build", "twine"],
    },
)