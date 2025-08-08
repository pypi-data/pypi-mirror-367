from setuptools import setup, find_packages

setup(
    name="qa_trainer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "simpletransformers>=0.64.3",
        "optuna",
        "torch",
        "transformers"
    ],
    author="Your Name",
    description="Train QA models from feedback with Optuna hyperparameter tuning",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
