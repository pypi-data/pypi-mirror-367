#!/usr/bin/env python

import setuptools

setuptools.setup(
    name="llama2-lora-adapter",
    version="0.1.0",
    author="danny laurent",
    author_email="your_email@example.com",
    description="LoRA adapter for Llama2",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://huggingface.co/dze1818/llama2-lora-adapter",
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "transformers>=4.0.0",
        "peft>=0.4.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

