from setuptools import setup, find_packages

setup(
    name='horseracepredictor',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'scikit-learn'
    ],
    author='Deviprasad Gurrana',
    description='A horse race prediction package using linear regression',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/DeviprasadGurrana/horseracepredictor.git',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.7',
)
