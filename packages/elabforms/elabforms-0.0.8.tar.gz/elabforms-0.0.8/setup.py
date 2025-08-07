from setuptools import setup, find_packages
import os

root_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root_dir, "VERSION")) as version_file:
    version = version_file.read().strip()

with open(os.path.join(root_dir, 'requirements.txt')) as f:
    requires = f.read().splitlines()

with open(os.path.join(root_dir, 'README.md')) as f:
    long_description = f.read()

setup(
    name="elabforms",
    version=version,
    packages=find_packages(where="."),
    author="Fatai Idrissou, Sylvain Takerkart",
    description="A set of tools to create and manage standardized forms for eLabFTW",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    install_requires=requires,
    include_package_data=True,
    python_requires='>=3.8',
    extras_require={
        'test': ['pytest', 'flake8'],
    },
    entry_points={
        "console_scripts": [
            "eform=elabforms.cli:cli"
        ],
    },
)
