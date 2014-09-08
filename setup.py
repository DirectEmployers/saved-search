from distutils.core import setup
from setuptools import find_packages

setup(
    name="saved_search",
    version="0.3",
    description="User-defined, persistent searches for Django-Haystack.",
    author="Matt DeBoard",
    author_email="matt@directemployers.com",
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search'
    ],
)
