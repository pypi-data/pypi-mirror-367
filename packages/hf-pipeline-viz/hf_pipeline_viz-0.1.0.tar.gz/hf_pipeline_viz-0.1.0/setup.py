from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    description = f.read()

setup(
    name="hf_pipeline_viz",
    version="0.1.0",
    description="Attention heat-map helper for Hugging Face text-generation pipelines",
    author="Vaibhav Gupta",
    author_email="vaibhavguptaq8@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "transformers",
        "torch",
        "numpy",
        "matplotlib",
    ],
    long_description=description,
    long_description_content_type="text/markdown",
)
