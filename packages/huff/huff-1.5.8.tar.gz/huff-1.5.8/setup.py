from setuptools import setup, find_packages
import os

def read_README():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        return f.read()
    
setup(
    name='huff',
    version='1.5.8',
    description='huff: Huff Model Market Area Analysis',
    packages=find_packages(include=["huff", "huff.tests"]),
    include_package_data=True,
    long_description=read_README(),
    long_description_content_type='text/markdown',
    author='Thomas Wieland',
    author_email='geowieland@googlemail.com',
    license_files=["LICENSE"],
    package_data={
        'huff': ['tests/data/*'],
    },
    install_requires=[
        'geopandas==0.14.4',
        'pandas==2.2.3',
        'numpy==1.26.3',
        'statsmodels==0.14.1',
        'shapely==2.0.4',
        'requests==2.31.0',
        'matplotlib==3.8.2',
        'pillow==10.2.0',
        'contextily==1.6.2',
        'openpyxl==3.1.4'
    ],
    test_suite='tests',
)