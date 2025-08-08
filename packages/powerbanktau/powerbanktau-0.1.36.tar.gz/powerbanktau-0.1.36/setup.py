from setuptools import setup, find_packages
import os


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='powerbanktau',
    version='0.1.36',
    description='A example Python package',
    packages=find_packages(),  # Automatically finds your package

    # url='https://github.com/shuds13/pyexample',
    author='Nicolas Lynn',
    author_email='nicolaslynn@mail.tau.ac.il',
    license='BSD 2-clause',
    scripts=[os.path.join('powerbanktau/scripts', file) for file in os.listdir('powerbanktau/scripts')],  # List all your scripts here

    install_requires=requirements,

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',

    ],
)