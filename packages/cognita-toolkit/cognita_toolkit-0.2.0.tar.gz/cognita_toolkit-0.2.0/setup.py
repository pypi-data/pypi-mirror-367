from setuptools import setup, find_packages

setup(
    name='cognita-toolkit',
    version='0.2.0',
    author='Aditya Kharat',
    description='A symbolic reasoning toolkit for building logic-driven agents and AGI research.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
