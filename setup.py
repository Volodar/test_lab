import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="test_lab",
    version=0.11,
    author="Vladimir Tolmachev",
    author_email="tolm_vl@hotmail.com",
    description="A tool to test apps on mobile devices and PC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Volodar/test_lab",
    packages=setuptools.find_packages(exclude=("unit_tests",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)