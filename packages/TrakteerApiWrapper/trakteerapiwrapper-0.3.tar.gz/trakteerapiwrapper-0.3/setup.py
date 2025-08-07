from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='TrakteerApiWrapper',
    version='0.3',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='Indra Bagus',
    author_email='indrabusiness00@gmail.com',
    description='A simple wrapper for the Trakteer API',
    long_description=description,
    long_description_content_type='text/markdown',
    url='https://github.com/IndraBagus0/TrakteerApiWrapper',
    keywords=['trakteer', 'api', 'wrapper', 'python'],
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',    
    ]
)