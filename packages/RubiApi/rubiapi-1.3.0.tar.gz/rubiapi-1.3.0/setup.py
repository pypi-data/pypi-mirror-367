from setuptools import setup, find_packages

try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ''

setup(
    name='RubiApi',
    version='1.3.0',
    description='A Python library for interacting with Rubika Bot API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='ali jafari',
    author_email='thealiapi@gmail.com',
    maintainer='ali jafari',
    maintainer_email='thealiapi@gmail.com',
    url='https://github.com/iTs-GoJo/RubiApi',
    download_url='https://github.com/iTs-GoJo/RubiApi/archive/refs/tags/v0.1.0.tar.gz',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries',
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
    ],
)
