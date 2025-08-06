from setuptools import setup, find_packages

setup(
    name='adiff',
    version='2.0.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'tabulate',
        'lxml',
        'openpyxl'
    ],
    entry_points={
        'console_scripts': [
            'adiff=adiff.cli:main',
        ],
    },
    author='Ashish',
    author_email='ashishaxm@gmail.com',
    description='Advanced XML Comparison CLI Tool',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ashishnxt/adiff',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Topic :: Text Processing :: Markup :: XML',
        'Intended Audience :: Developers'
    ],
    python_requires='>=3.6',
)

