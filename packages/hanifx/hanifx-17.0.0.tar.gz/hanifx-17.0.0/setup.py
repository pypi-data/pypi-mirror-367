
from setuptools import setup, find_packages

setup(
    name='hanifx',
    version='17.0.0',
    author='Hanif',
    author_email='sajim4653@gmail.com',
    description='Custom encryption and decryption module using unique HanifX alphabet',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/hanifx/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
