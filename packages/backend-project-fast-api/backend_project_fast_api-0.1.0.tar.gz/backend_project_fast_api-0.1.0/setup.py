from setuptools import setup, find_packages

setup(
    name="backend_project_fast_api",
    version="0.1.0",
    author="Jan Proczek",
    author_email="jan@example.com",
    description="Prosta aplikacja FastAPI",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn"
    ],
    entry_points={
        "console_scripts": [
            "runapp=backend_project_fast_api.main:app"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)