from setuptools import setup, find_packages

setup(
    name='alak',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'lark',
    ],
    entry_points={
        'console_scripts': [
            'alak = alak.cli:main',
        ],
    },
    author="leetz-kowd",
    description="A Tagalog-inspired esolang based on inuman culture.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)