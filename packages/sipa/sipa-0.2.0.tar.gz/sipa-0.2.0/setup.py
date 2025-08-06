from setuptools import setup, find_packages

with open("README_PyPI.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sipa",
    version="0.2.0",
    author="Haydar Kadıoğlu",
    author_email="a.haydar.kadioglu@gmail.com",  
    description="Simple Image Processing Application - A GUI-based image processing tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/haydarkadioglu/simple-image-processing-application",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "matplotlib>=3.3.0",
        "PyQt5>=5.15.0",
        "opencv-python>=4.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "sipa=sipa.main:main",
        ],
    },
    keywords="image-processing, gui, pyqt5, computer-vision, image-filters",
    project_urls={
        "Bug Reports": "https://github.com/haydarkadioglu/simple-image-processing-application/issues",
        "Source": "https://github.com/haydarkadioglu/simple-image-processing-application",
    },
)
