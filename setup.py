import setuptools, os
from distutils.core import setup

from sqlchain.version import *

try:
   import pypandoc
   readme_md = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
   readme_md = open('README.md').read()

destdir = os.path.join('share','sqlchain')
datafiles = [(os.path.join(destdir,d), [os.path.join(d,f) for f in files]) for d, folders, files in os.walk('www')]
datafiles.extend([(os.path.join(destdir,d), [os.path.join(d,f) for f in files]) for d, folders, files in os.walk('etc')])
   
setup(
    name='sqlchain',
    packages=['sqlchain'],
    version=version,
    author='neoCogent.com',
    author_email='info@neocogent.com',
    url='https://github.com/neocogent/sqlchain',
    download_url='https://github.com/neocogent/sqlchain/tarball/'+version,
    license='MIT',
    classifiers=[
    #'Development Status :: 3 - Alpha',
    'Development Status :: 4 - Beta',
    #'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Operating System :: POSIX :: Linux',
    'Topic :: Database :: Database Engines/Servers',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
    'Topic :: Office/Business :: Financial',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7'
    ],
    keywords='bitcoin sql blockchain api websocket rpc server',
    description='Compact SQL layer for Bitcoin blockchain.',
    long_description=readme_md,
    scripts=['sqlchaind','sqlchain-api','sqlchain-electrum','sqlchain-config'],
    install_requires=[
        "gevent >= 1.2.0",
        "gevent-websocket >= 0.9.5",
        "python-daemon >= 1.5.5",
        "MySQL-python >= 1.2.5",
        "python-bitcoinrpc >= 0.1",
        "backports.functools_lru_cache >= 1.2.1",
        "python2-pythondialog >= 3.4.0"
    ],
    data_files=datafiles

)
