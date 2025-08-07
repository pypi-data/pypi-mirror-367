from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='financial_dataset_preprocessor',
    version='0.4.5',
    packages=find_packages(),
    install_requires=required,
    author='June Young Park',
    author_email='juneyoungpaak@gmail.com',
    description='A package for preprocessing financial datasets, powering the Life Asset Management development team.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nailen1/financial_dataset_preprocessor',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.11',
)