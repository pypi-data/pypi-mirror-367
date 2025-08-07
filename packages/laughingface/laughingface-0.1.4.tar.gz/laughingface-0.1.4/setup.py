from setuptools import setup, find_packages

setup(
    name="laughingface",
    version="0.1.4",
    description="A library for managing and invoking AI modules with LaughingFace.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/laughingface",  # Replace with your GitHub repository
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.0",
        "litellm>=0.1.0"  # Replace with the actual LiteLLM version
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
