from setuptools import setup, find_packages

setup(
    name="printpop",
    version="0.2.2",
    packages=find_packages(),  # Auto-discovers the 'printpop' folder
    entry_points={
        "console_scripts": [
            "printpop = printpop.core:main",
        ]
    },
    include_package_data=True
)