from setuptools import setup, find_packages

setup(
    name="detaillogger",
    version="0.2.0",
    packages=find_packages(),  # This auto-discovers the 'detaillogger' folder
    entry_points={
        "console_scripts": [
            "detaillogger = detaillogger.core:main",
        ]
    },
    include_package_data=True,
)