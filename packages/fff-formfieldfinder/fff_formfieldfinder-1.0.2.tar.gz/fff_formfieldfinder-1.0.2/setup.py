from setuptools import setup, find_packages

setup(
    name="fff-formfieldfinder",
    version="1.0.2",
    description="Form Field Finder: Extracts login fields and form action for fuzzing",
    author="[Ph4nt01]",
    author_email="ph4nt0.84@gmail.com",
    url="https://github.com/Ph4nt01/FFF-FormFieldFinder",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "requests",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "fff=fff.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
)
