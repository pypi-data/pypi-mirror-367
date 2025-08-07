import setuptools

setuptools.setup(
    name="tocaro-client",
    version="0.1.1",
    author="Jan Janssen",
    author_email="Jan.Janssen@dfki.de",
    description="Client to connect to the ToCaro Platform",
    long_description="README.md",
    url="",
    repository="",
    install_requires=["requests", "dataclasses-json"],
    tests_require=["pytest", "pytest-docker", "pytest-ordering", "random_dict"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    license_file="LICENSE",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
