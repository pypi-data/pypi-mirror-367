from setuptools import setup, find_namespace_packages

setup(
    name="st-image-carousel",
    version="0.1.4",
    author="Antoine Verdon",
    author_email="antoineverdon.pro@gmail.com",
    description="Un composant Streamlit pour afficher un carrousel d'images",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/2nzi/st_image_carousel",
    packages=find_namespace_packages(include=["st_image_carousel", "st_image_carousel.*"]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "streamlit >= 0.63",
    ],
)
