from setuptools import setup, find_packages

setup(
    name="revdownloader",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "beautifulsoup4>=4.9.3",
        "python-dotenv>=0.19.0",
    ],
    python_requires=">=3.7",
    author="Tu Nombre",
    author_email="tu@email.com",
    description="Librería para descarga de archivos",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/revdownloader",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
