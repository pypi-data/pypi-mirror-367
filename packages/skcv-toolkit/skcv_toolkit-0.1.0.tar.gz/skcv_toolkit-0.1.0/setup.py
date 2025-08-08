from setuptools import setup, find_packages

setup(
    name="skcv-toolkit",
    version="0.1.0",
    description="Santhosh Kumar Computer Vision Toolkit - A comprehensive computer vision toolkit for image processing and analysis",
    author="Santhosh Kumar",
    author_email="santhoshkumarsampath.off@gmail.com",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "opencv-python>=4.5.0",
        "matplotlib>=3.3.0",
        "Pillow>=8.0.0",
        "scikit-image>=0.18.0",
        "scipy>=1.7.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
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
    ],
)
