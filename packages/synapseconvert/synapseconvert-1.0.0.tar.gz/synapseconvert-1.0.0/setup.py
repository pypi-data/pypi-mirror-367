from setuptools import setup, find_packages

setup(
    name="synapseconvert",
    version="1.0.0",  # ✅ Incremented for PyPI release
    author="Samuel Baylis",
    author_email="request@biblicalstory.org",
    description="Tools for converting Synapse RTP JSON to spreadsheet and back.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/BiblicalStory/synapseconvert",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "synapseconvert": ["templates/*"],  # ✅ Include templates folder
    },
    install_requires=[
        "pandas",
        "openpyxl"
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'synapse-upconvert = synapseconvert.upconvert:main',
            'synapse-downconvert = synapseconvert.downconvert:main'
        ]
    },
)
