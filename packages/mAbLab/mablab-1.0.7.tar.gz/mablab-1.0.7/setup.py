from setuptools import setup, find_packages

setup(
    name="mAbLab",
    version="1.0.7",
    author="R. Paul Nobrega",
    author_email="paul@paulnobrega.net",
    description="A library for analyzing monoclonal antibody characteristics by domain.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/PaulNobrega/mAbLab",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "antpack==0.3.6.1",
        "biopython==1.84",
        "numpy==2.1.3",
        "Levenshtein==0.26.1",
        "ImmuneBuilder==1.2",
        "pandas==2.2.3",
        "scipy==1.14.1",
        "torch==2.5.1",
        "torchvision==0.20.1",
        "torchaudio==2.5.1",
    ],
)
