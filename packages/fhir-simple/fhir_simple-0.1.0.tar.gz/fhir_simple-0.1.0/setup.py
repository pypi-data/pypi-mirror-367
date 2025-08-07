from setuptools import setup, find_packages

setup(
    name="fhir_simple",
    version="0.1.0",
    author="Bhushan Varade",
    author_email="bvarade02@gmail.com",
    description="A library to simplify FHIR Patient objects to basic JSON.",
    packages=find_packages(),
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="fhir patient json healthcare",
)
