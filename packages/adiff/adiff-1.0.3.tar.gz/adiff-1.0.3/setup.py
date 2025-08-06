from setuptools import setup, find_packages

setup(
    name='adiff',
    version='1.0.3',
    description='A tool to diff multiple XML files',
    author='Ashish',
    author_email='ashishaxm11@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'openpyxl',
        'lxml',
        'tabulate'
    ],
    entry_points={
        'console_scripts': [
            'adiff = adiff.__main__:main'
        ]
    },
)

