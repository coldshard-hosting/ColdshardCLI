from setuptools import setup

setup(
    name='coldshard-cli',
    version='0.1.0',
    packages=["cli", "cli.utils"],
    install_requires=[
        'Click',
        "Requests",
    ],
    entry_points={
        'console_scripts': [
            'coldshard = cli.main:core',
        ],
    },
)
