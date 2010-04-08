from distutils.core import setup

setup(
    name='sql_interp',
    version='0.1.0',
    author='Michael Hampton',
    author_email='mirhampt@gmail.com',
    packages=['sql_interp'],
    url='http://bitbucket.org/mirhampt/sql_interp/',
    license='MIT',
    description='Interpolate Python variables into SQL statements.',
    long_description=open('README').read(),
    keywords='sql interpolation database',
)
