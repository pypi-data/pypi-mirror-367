from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name='pyqt5-calculator0.1',
    version='0.1.0',
    author="Arnoldas A.",
    author_email="ambrasas.arnoldas@gmail.com",
    url="https://github.com/Asasai001/calculator",
    description='Simple PyQt5 calculator application',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyQt5'
    ],
    python_requires='>=3.7'
)