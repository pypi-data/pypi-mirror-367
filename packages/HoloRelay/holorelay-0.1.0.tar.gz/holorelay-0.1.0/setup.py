# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="HoloRelay",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "AgentToAgent",
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description="A modern way to let AI-agents Communicate",
)
