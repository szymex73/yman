from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="yman",
    version="1.0.1",
    author="szymex73",
    license="MIT",
    author_email="szymex73@gmail.com",
    description="Yakuake session management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/szymex73/yman",
    packages=find_packages(),
    install_requires=['click', 'dasbus'],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': ['yman = yman.cli:cli']
    }
)
