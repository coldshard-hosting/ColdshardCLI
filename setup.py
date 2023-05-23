from setuptools import setup

setup(
    name="coldshard-cli",
    version="0.1.3",
    packages=["cli", "cli.utils"],
    install_requires=[
        "asyncclick",
        "git+https://github.com/PteroPackages/Pytero",
        "Inquirer",
    ],
    entry_points={
        "console_scripts": [
            "coldshard = cli.main:core",
        ],
    },
    author_email="TheUntraceable@TheUntraceable.me",
    author="ColdShard LLC",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
)
