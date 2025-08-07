from setuptools import setup, find_packages

setup(
    name="agomax",
    version="0.1.0",
    description="Drone anomaly detection package",
    author="shaguntembhurne",
    author_email="your@email.com",
    url="https://github.com/shaguntembhurne/agomax",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "scikit-learn"
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'agomax=cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
