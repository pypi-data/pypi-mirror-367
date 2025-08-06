from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='APICORE_Python',
    version='1.0.1',
    packages=find_packages(),
    description='A Python library for parsing API configuration files following the APICORE specification',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='SRInternet-Studio',
    author_email='srinternet@qq.com',
    license='MIT',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
