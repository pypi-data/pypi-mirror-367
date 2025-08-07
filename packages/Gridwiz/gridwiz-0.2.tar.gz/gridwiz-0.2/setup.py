from setuptools import setup, find_packages

setup(
    name='Gridwiz',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'openpyxl',
        'numpy'
    ],
)
