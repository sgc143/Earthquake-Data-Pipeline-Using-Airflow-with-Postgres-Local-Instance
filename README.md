# Earthquake Data Pipeline Using Airflow with Postgres Local Instance
Python, Flask, PostgreSQL

## ETL data pipeline fetching data using USGS API API, transforming data then loading to postgres
- Flask web application with dashboard interface
- Airflow DAG tasks as Python pipeline class
- Set up PostgreSQL database with proper table structure
- Built pipeline monitoring and status tracking system

### GitHub repositories don't handle PostgreSQL databases directly. 
However, GitHub Codespaces can automatically set up PostgreSQL through the devcontainer configuration.

## Basic architecture:

GitHub Codespaces + PostgreSQL

### Resources set up:

.devcontainer/devcontainer.json automatically installs PostgreSQL when the Codespace starts
Pre-configured environment variables point to the local PostgreSQL instance
Database gets created automatically when you run the application

### Workflow:
To run: Launch Github codespaces
PostgreSQL installs automatically (takes 1-2 minutes)
The app connects to localhost:5432 with the configured credentials
Database and tables are created on first run

For the persisten database option, see other repo.
