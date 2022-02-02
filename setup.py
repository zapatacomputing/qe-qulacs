import site
import sys
import warnings

import setuptools

# Workaound for https://github.com/pypa/pip/issues/7953
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

try:
    from subtrees.z_quantum_actions.setup_extras import extras
except ImportError:
    warnings.warn("Unable to import extras")
    extras = {}

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="qe-qulacs",
    use_scm_version=True,
    author="Zapata Computing, Inc.",
    author_email="info@zapatacomputing.com",
    description="Qulacs backend for Orquestra.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zapatacomputing/qe-qulacs",
    packages=setuptools.find_packages(where="src/python"),
    package_dir={"": "src/python"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    setup_requires=["setuptools_scm~=6.0"],
    install_requires=[
        "cmake>=3.18",
        "gcc7==0.0.7",  # The latest version 0.0.9 only has wheels for Mac
        "qulacs==0.2.0",
        "z-quantum-core",
    ],
    extras_require=extras,
    package_data={"src/python": ["py.typed"]},
    zip_safe=False,
)
