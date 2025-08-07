from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='Topsis-Paras-102203836',
    packages=find_packages(),
    version='1.0.6',
    description='A Python package for TOPSIS',
    long_description=long_description,  
    long_description_content_type='text/markdown',  
    author='Paras Jain',
    author_email='pjain3_be22@thapar.edu',
    url='https://github.com/ParasJain19/Topsis-PARAS-102203836',
    download_url='https://github.com/ParasJain19/Topsis-PARAS-102203836/archive/v1.0.0.tar.gz',
    keywords=['Topsis', 'Ranking', 'Decision Making', 'MCDM'],
    install_requires=[
        'pandas',
        'numpy',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],



)
