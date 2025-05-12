from setuptools import setup, find_packages

setup(
    name="robinhood_algo",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'pandas>=1.3.0',
        'robin-stocks>=2.0.3',
        'pyyaml>=5.4.1',
        'scipy>=1.7.0',
        'qmcpy>=1.3.0'
    ],
    python_requires='>=3.8',
)