import setuptools
import os

readme_path = os.path.join("..", "README.md")
with open(readme_path, "r") as f:
    long_description = f.read()

setuptools.setup(
    name="qe-qulacs",
    version="0.1.0",
    author="Zapata Computing, Inc.",
    author_email="info@zapatacomputing.com",
    description="Qulacs backend for Orquestra.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zapatacomputing/qe-qulacs",
    packages=setuptools.find_packages(where='src/python'),
    package_dir={'' : 'python'},
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        "cmake>=3.18",
        "gcc7==0.0.7", # The latest version 0.0.9 only has wheels for Mac
        "qulacs==0.1.10.1",
        "z-quantum-core"
    ],
)
