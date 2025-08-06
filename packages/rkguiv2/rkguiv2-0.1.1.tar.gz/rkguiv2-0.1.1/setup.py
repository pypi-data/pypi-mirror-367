from setuptools import setup, find_packages

setup(
    name="rkguiv2",
    version="0.1.1",
    author="11iii",
    author_email="11iiimnjup@gmail.com",
    description="A Just GUI on Python",
    long_description="GUI on Python",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "pywebview>=3.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
)
