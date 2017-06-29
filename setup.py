from distutils.core import setup

from aptos import __version__

setup(
    name='aptos',
    version=__version__,
    author='Jason Walsh',
    maintainer='Jason Walsh',
    url='https://github.com/pennsignals/aptos',
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
    license='License :: OSI Approved :: MIT License',
    packages=['aptos']
)
