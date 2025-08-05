from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
# long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="st-image-carousel",
    version="0.0.13",
    author="Antoine",
    author_email="xxx@gmail.com",
    description="A modern Streamlit component for creating interactive image carousels",
    long_description="",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(exclude=["st_image_carousel.frontend.build"]),
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
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest==7.4.0",
            "playwright==1.48.0",
            "requests==2.31.0",
            "pytest-playwright-snapshot==1.0",
            "pytest-rerunfailures==12.0",
        ]
    }
)