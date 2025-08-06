from setuptools import setup, find_packages

setup(
    name='pycalculator-aniket',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    author='ANiket Patidar',
    author_email='aniketpatidar70@gmail.com',
    description='A full-featured Python calculator package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/aniket-patidar01/py',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)


