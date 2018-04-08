from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='find_store',  

    version='1.0.0',  

    description='Locate the nearest store and print the matching store address and distance',  

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=['docopt', 'googlemaps', 'pandas', 'numpy'],  

    entry_points={  
        'console_scripts': [
            'find_store=find_store.main:main',
        ],
    },

    include_package_data=True
)
