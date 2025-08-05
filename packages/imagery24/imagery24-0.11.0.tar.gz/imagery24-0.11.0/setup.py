from setuptools import find_packages, setup

setup(
    name="imagery24",
    version="0.11.0",
    packages=find_packages(),
    description="A short description of your package",
    long_description_content_type="text/markdown",
    author_email="your.email@example.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "rasterio==1.4.3",
        "pillow==11.1.0",
        "imagecodecs==2024.12.30",
        "geopandas==1.0.1",
        "matplotlib==3.10.0",
        "pykml==0.2.0",
        "centerline==1.1.1",
        "networkx==3.4.2",
        "shapely==2.1.1",
    ],
    zip_safe=True,
)
