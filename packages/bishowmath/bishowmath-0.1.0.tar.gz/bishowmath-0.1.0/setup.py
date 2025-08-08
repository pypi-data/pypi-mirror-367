from setuptools import setup, find_packages

setup(
    name='bishowmath',
    version='0.1.0',
    description='A simple math library for basic arithmetic',
    author='Bishwa Ghimire',
    author_email='bishowghi2061.email@example.com',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    test_suite='tests',
)
