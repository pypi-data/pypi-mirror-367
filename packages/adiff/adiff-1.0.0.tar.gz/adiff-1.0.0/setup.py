from setuptools import setup, find_packages

setup(
    name='adiff',  # 👈 this is the pip install name
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'tabulate',
        'lxml',
        'openpyxl'
    ],
    entry_points={
        'console_scripts': [
            'vdiff=vdiff.cli:main',  # 👈 this makes `vdiff` CLI command
        ],
    },
    author='Ashish',
    author_email='ashishaxm@gmail.com',
    description='Compare multiple XML files with Excel output and summary statistics',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ashishnxt/vdiff',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: Markup :: XML',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.6',
)

