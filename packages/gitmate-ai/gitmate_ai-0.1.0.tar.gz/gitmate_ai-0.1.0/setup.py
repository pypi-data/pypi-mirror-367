from setuptools import setup, find_packages

setup(
    name="gitmate-ai",
    version="0.1.0",
    description="GitMate - AI Git Assistant for Terminal",
    author="Tejas Raundal",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gitmate=gitmate.cli:main',
        ],
    },
    install_requires=[
        "rich",
        "langchain",
        "langchain-google-genai",
        "langchain-openai",
        "langchain-anthropic",
    ],
    python_requires='>=3.8',
)
