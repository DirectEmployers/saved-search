from distutils.core import setup

setup(
    name = "saved_search",
    version = "0.1",
    description = "User-defined, persistent searches for Django-Haystack.",
    author = "Matt DeBoard",
    author_email = "matt@directemployers.com",
    py_modules = ['saved_search'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search'
    ],
)