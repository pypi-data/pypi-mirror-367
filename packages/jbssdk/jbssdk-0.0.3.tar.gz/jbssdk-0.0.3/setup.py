from setuptools import setup, find_packages

setup(
    name='jbssdk',
    version='0.0.3',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
)