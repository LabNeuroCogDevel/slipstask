import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="soapy",
    version="0.0.3", # 20200730 - animals
    author="Will Foran",
    author_email="willforn+py@gmail.com",
    description="Slips of action/Fabulious Fruits task",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LabNeuroCogDevel/slipstask",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'psychopy',
        'typing',
    ],
    include_package_data=True,
    scripts=['soapy/bin/SOA'],
)
