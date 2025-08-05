from setuptools import setup, find_namespace_packages

setup(
    name="st-image-carousel",  # <= important : tirets pour PyPI
    version="0.1.0",
    author="Ton Nom",
    author_email="ton.email@example.com",
    description="Un composant Streamlit pour afficher un carrousel d’images",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/2nzi/st-image-carousel",  # ton repo
    packages=find_namespace_packages(include=["st_image_carousel", "st_image_carousel.*"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
