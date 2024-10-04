from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") 

setup(
    name='qab',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'uiautomator2',
    ],  # Add a comma here
    author='joman2',
    description='low-code quality assurance bot framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
     project_urls={
           'Source Repository': 'https://github.com/joman2/qab/'
    }
)