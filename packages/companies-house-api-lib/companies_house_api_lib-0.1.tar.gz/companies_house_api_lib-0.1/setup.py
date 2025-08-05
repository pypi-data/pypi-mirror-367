from setuptools import setup, find_packages

setup(
    name='companies-house-api-lib',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='Ali Gardezi',
    author_email='aagardezi+github@gmail.com',
    description='A Python client for the Companies House API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/aagardezi/companies-house-api-lib',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
