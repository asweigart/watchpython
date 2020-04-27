import io
import os
import re
from setuptools import setup, find_packages

scriptFolder = os.path.dirname(os.path.realpath(__file__))
os.chdir(scriptFolder)

# Find version info from module (without importing the module):
with open('src/watchpython/__init__.py', 'r') as fo:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fo.read(), re.MULTILINE).group(1)

# Use the README.md content for the long description:
with io.open('README.md', encoding='utf-8') as fo:
    long_description = fo.read()

setup(
    name='WatchPython',
    version=version,
    url='https://github.com/asweigart/watchpython',
    author='Al Sweigart',
    author_email='al@inventwithpython.com',
    description=('''A re-implementation of the Unix watch command in Python.'''),
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    test_suite='tests',
    install_requires=[],
    keywords='',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
)
