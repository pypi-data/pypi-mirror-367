from setuptools import setup, find_packages

setup(
    name="eyad123",         # Your unique package name
    version="0.3",
    packages=find_packages(),
    install_requires=[
        "flask",                        # This makes pip install Flask automatically
    ],
    author="Eyad123",
    description="My hello world package that depends on Flask",
    long_description="A simple example package that installs Flask automatically.",
    long_description_content_type="text/plain",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
