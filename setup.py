from distutils.core import setup
import setuptools
from os import path


__version__ = '1.1.1'


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='veracross_api',
    packages=['veracross_api'],
    version=__version__,
    description='Simple library for interacting with the Veracross API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT License',
    author='Forrest Beck, Matthew Denaburg',
    author_email='forrest.beck@da.org, matthew.denaburg@ssfs.org',
    url='https://bitbucket.org/ssfs_tech/veracross_api',
    download_url=f'https://bitbucket.org/ssfs_tech/veracross_api/get/v{__version__}.tar.gz',
    keywords=['Veracross', 'API'],
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
)
