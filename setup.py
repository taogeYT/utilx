import re
import ast
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('utilx/__init__.py', 'rb') as f:
    rs = _version_re.search(f.read().decode('utf-8')).group(1)
    version = str(ast.literal_eval(rs))

setup(
    name='utilx',
    py_modules=["utilx"],
    version=version,
    install_requires=['plan>=0.5', 'fire'],
    description='Python Toolkit',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
    ],
    author='yatao',
    url='https://github.com/taogeYT/utilx',
    author_email='li_yatao@outlook.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=False,
    zip_safe=True,
    entry_points={
        'console_scripts': ['utilx = utilx.cli:main']
    }
)
