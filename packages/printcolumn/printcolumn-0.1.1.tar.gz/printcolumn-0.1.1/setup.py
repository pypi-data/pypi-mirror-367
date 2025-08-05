from setuptools import setup, find_packages

setup(
    name="columnprint",
    version="0.1.1",
    packages=find_packages(),  # Auto-discovers the 'printpop' folder
    install_requires=[
        "printpop>=0.2.0", 
    ],
    entry_points={
        "console_scripts": [
            "columnprint = columnprint.core:main",
        ]
    },
    include_package_data=True
)