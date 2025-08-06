from setuptools import setup, find_packages

setup(
    name="autowriter",
    version="1.0.2",
    author="Mysra Ahmed",
    author_email="misragmalahmad@gmail.com@email.com",
    description="A human-like auto typer with GUI, dark mode, pause/wait keys, and live stats.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mysra-Ahmed/Python-auto-typer",
    packages=find_packages(),
    install_requires=["keyboard"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'autowriter=autowriter.__init__:main',
        ],
    },
    include_package_data=True
)


