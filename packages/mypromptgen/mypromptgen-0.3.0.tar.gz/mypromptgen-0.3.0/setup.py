from setuptools import setup, find_packages
import os
import re

# Get version from __init__.py
version_re = re.compile(r'__version__\s*=\s*"(.+)"')
with open(os.path.join("mypromptgen", "__init__.py")) as f:
    for line in f:
        if line.startswith('__version__'):
            version = version_re.match(line).group(1)

# Read requirements and long description
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="mypromptgen",
    version=version,
    author="Your Name",
    author_email="your@email.com",
    description="Package for generating AI prompts and answers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['mypromptgen.migrate', 'mypromptgen.qlora', 'mypromptgen.distill']),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mypromptgen = mypromptgen.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
