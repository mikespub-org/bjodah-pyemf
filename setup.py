#!/usr/bin/env python3

PKG_NAME = "pyemf"
# import pyemf

# exec(open('pyemfstructrecord.py').read())w
# import pyemfstructrecord as module

setup_kw = dict(
    name=PKG_NAME,
    version="2.1.2-alpha",
    description="pyemf is a pure python module that provides bindings for an ECMA-234 compliant vector graphics library",
    # long_description = long_description,
    # keywords = module.__keywords__,
    license="GPL-2",
    author="Rob McMullen",
    author_email="robm@users.sourceforge.net",
    url="http://github.com/6tudent/pyemf",
    platforms="any",
    # py_modules = [PKG_NAME],
    packages=[PKG_NAME],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Graphics",
    ],
)

if __name__ == "__main__":
    from setuptools import setup

    setup(**setup_kw)
