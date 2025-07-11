from setuptools import setup, find_packages

setup(
    name="earthquake-pipeline",
    version="1.0.0",
    description="Earthquake Data ETL Pipeline with Flask Web Interface",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "flask==3.1.1",
        "flask-sqlalchemy==3.1.1",
        "psycopg2-binary==2.9.10",
        "pandas==2.3.1",
        "requests==2.32.4",
        "python-dateutil==2.9.0.post0",
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)