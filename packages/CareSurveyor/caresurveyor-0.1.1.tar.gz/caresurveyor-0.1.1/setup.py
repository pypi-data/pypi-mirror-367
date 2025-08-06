from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="CareSurveyor",
    version="0.1.1",
    author="CareSurveyor Team",
    author_email="contact@caresurveyor.dev",
    description="Survey Automation Pipeline for Clinical Studies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/caresurveyor/caresurveyor",
    project_urls={
        "Bug Tracker": "https://github.com/caresurveyor/caresurveyor/issues",
        "Documentation": "https://caresurveyor.readthedocs.io/",
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=[
        "google-api-python-client>=2.0.0",
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=0.5.0",
        "google-auth-httplib2>=0.1.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    keywords="google-forms clinical-research survey automation medical healthcare",
    entry_points={
        "console_scripts": [
            "caresurveyor=CareSurveyor.cli:main",
        ],
    },
)
