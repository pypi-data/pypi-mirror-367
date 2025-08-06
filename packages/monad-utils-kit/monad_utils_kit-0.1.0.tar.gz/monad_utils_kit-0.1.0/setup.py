from setuptools import setup, find_packages

setup(
    name="monad-utils-kit",
    version="0.1.0",
    author="Naufel Aniq",
    author_email="aniqraaj786@gmail.com",
    description="CLI tools for interacting with Monad testnet",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    py_modules=["fingerprint"],
    entry_points={
        "console_scripts": [
            "fingerprint=fingerprint:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
)
