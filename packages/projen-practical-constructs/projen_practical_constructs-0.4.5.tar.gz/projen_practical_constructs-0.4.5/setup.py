import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "projen_practical_constructs",
    "version": "0.4.5",
    "description": "Constructs and utilities for managing projects (Python, NodeJS etc) with Projen enforcing solid build, test and linting structures",
    "license": "MIT",
    "url": "https://github.com/flaviostutz/projen-practical-constructs.git",
    "long_description_content_type": "text/markdown",
    "author": "Flavio Stutz<flaviostutz@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/flaviostutz/projen-practical-constructs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "projen_practical_constructs",
        "projen_practical_constructs._jsii"
    ],
    "package_data": {
        "projen_practical_constructs._jsii": [
            "projen-practical-constructs@0.4.5.jsii.tgz"
        ],
        "projen_practical_constructs": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "constructs>=10.4.2, <11.0.0",
        "jsii>=1.106.0, <2.0.0",
        "projen>=0.91.13, <0.92.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
