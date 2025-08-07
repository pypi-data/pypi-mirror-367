#!/usr/bin/env python
#
# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

import os.path

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README")) as f:
    description = f.read()

setup(
    name="oops",
    version="0.1.0",
    description="OOPS report model and default allocation/[de]serialization.",
    long_description=description,
    long_description_content_type="text/x-rst",
    license="LGPL v3",
    python_requires=">=3.8",
    author="Launchpad Developers",
    author_email="launchpad-dev@lists.launchpad.net",
    maintainer="Launchpad Developers",
    maintainer_email="launchpad-dev@lists.launchpad.net",
    url="https://launchpad.net/python-oops",
    packages=["oops"],
    package_dir={"": "."},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",  # noqa: E501
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=[
        "pytz",
    ],
    extras_require=dict(
        test=[
            "fixtures",
            "testtools",
        ]
    ),
)
