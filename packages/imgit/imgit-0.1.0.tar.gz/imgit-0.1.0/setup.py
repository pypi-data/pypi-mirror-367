from setuptools import setup, find_packages
import os

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

setup(
    name='imgit',
    version='0.1.0',
    packages=find_packages(),
    py_modules=['imgit'],
    entry_points={
        'console_scripts': [
            'imgit = imgit:main',
        ],
    },
    install_requires=[
        'GitPython>=3.1.0',
        'ruamel.yaml>=0.17.0',
        'pyyaml>=6.0',
        'prettytable>=3.0.0',
        'progress>=1.5',
        'runcmd>=0.4',
    ],
    author='Your Name',
    author_email='your.email@example.com',
    description='Git仓库管理自动化工具',
    long_description=read_file('README.md') if os.path.exists('README.md') else 'Git repository management automation tool',
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/imgit',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)