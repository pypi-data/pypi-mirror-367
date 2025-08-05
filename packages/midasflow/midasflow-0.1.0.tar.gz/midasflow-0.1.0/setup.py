import setuptools

with open("README.md") as f:
    long_description = f.read().rstrip()

with open("midasflow/VERSION") as f:
    version = f.read().rstrip()

setuptools.setup(
    name="midasflow",
    version=version,
    license="GPLv3+",
    author="Huidae Cho",
    author_email="grass4u@gmail.com",
    description="MIDASFlow is the Python package for the Memory-Efficient I/O-Improved Drainage Analysis System (MIDAS).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HuidaeCho/midasflow",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3",
    package_data={"midasflow": ["VERSION", "midasflow.db"]},
    entry_points={"console_scripts": ["midasflow=midasflow:main"]},
)
