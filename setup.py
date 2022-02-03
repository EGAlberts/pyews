import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyews",
    version="1.0.3",
    author="Elvin Alberts",
    author_email="elvingalberts@gmail.com",
    description="Interface to the dana EWS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EGAlberts/py-ews",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)