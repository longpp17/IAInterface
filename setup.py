import setuptools

from setuptools import setup

setup(
    name="YourProjectName",
    version="0.1",
    description="Your project description",
    author="Your Name",
    author_email="your.email@example.com",
    packages=["your_package_name"],  # Replace with your actual package names
    install_requires=[
        "pyaudio",  # PyAudio for audio I/O
        "socket",  # For network socket programming
    ],
    classifiers=[
        "Development Status ::  3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python ::  3",
        "Operating System :: OS Independent",
    ],
)
