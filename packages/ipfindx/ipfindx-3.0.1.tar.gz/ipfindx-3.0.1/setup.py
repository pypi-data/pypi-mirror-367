#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='ipfindx',
    version='3.0.1',
    author='Alex Butler',
    description='Advanced IP Intelligence Toolkit for cybersecurity professionals',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/VritraSecz/IPFindX',
    project_urls={
        'Bug Reports': 'https://github.com/VritraSecz/IPFindX/issues',
        'Source': 'https://github.com/VritraSecz/IPFindX',
        'Documentation': 'https://github.com/VritraSecz/IPFindX#readme',
        'Website': 'https://vritrasec.com',
    },
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'Topic :: System :: Networking',
        'Topic :: Internet',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Environment :: Console',
        'Natural Language :: English',
    ],
    keywords='ip intelligence geolocation osint cybersecurity network security threat-intelligence ip-lookup cybersec infosec penetration-testing',
    python_requires='>=3.7',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'ipfindx=ipfindx.ipfindx:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    license='MIT',
    platforms=['any'],
)
