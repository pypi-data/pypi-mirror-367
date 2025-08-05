from setuptools import setup, find_packages

setup(
    name='kleenscan',
    version='0.6.0',
    packages=find_packages(),
    install_requires=[
        'toml',
        'pyyaml',
        'requests',
        'sty'
    ],
    entry_points={
        'console_scripts': [
            'kleenscan=kleenscan.cli:main',  # 'command-name=package.module:function'
        ],
    },
    author='Kleenscan',
    author_email='ksdev01@gmail.com',
    description='Kleenscan command line application and API wrapper library.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ksdev01/kleenscan-cli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)