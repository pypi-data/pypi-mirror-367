from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="phoney",
    version="0.2.6",
    description="Fake Info generator, a library for generating realistic personal data like names, phone numbers, emails, and more.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="rarfile",
    author_email="d7276250@email.com",
    url="https://github.com/YTstyo/phoney",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
