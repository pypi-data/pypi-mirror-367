# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="HoloCapture",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "opencv-python",
        "numpy",
        "Pillow",
        "MediaCapture"
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description="An easy way to capture and stream media from multiple cameras and from the screen",
)
