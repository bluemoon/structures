from setuptools import setup, find_packages
import os
import sys

VERSION = "0.0.1.6"
setup(
    name = "bm_structures",
    version = VERSION,
    packages = [
    'bm_structures',

    ],
    
    package_dir = {'bm_structures' : 'src'},
    zip_safe=False,
    include_package_data=True,
    license='GPL',
    author='Alex Toney',
    author_email='toneyalex@gmail.com',
    description='Common structures for python',
    #test_suite="nose.collector",
    #tests_require="nose",
)
