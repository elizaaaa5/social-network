from setuptools import setup, find_packages

setup(
    name="user-service",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "sqlalchemy",
        "python-jose[cryptography]",
        "psycopg2-binary",
        "pydantic[email]"
    ],
)
