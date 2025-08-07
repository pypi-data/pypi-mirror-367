from setuptools import setup, find_packages

setup(
    name="agomax",
    version="0.1.3",
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
    include_package_data=True,
    package_data={
        'drone_anomoly': ['data/*.csv', 'data/*.txt'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
