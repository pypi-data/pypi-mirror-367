from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='xlsxlean',
    version='0.1.0',
    description='Minimal memory XLSX reader with safe preview and full content options',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Animesh Ranjan',
    author_email='ranjananimesh5@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=['psutil'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
