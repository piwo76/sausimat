import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sausimat",
    version="0.0.2",
    author="piwo",
    author_email="piwo76@gmail.com",
    description="Musicbox",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://https://github.com/piwo76/sausimat",
    packages=setuptools.find_packages(),
    install_requires=[
        'python-mpd2',
        'serial'
    ],
    python_requires='>=3.6.0',
    entry_points={
        'console_scripts': ['sausimat=sausimat.start:run', 'rescan_library=sausimat.start:rescan_library', 'create_playlist=sausimat.start:create_playlist'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)