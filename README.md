# Earthquake Data Pipeline

A Flask-based web application that manages an earthquake data ETL pipeline, successfully converted from a Docker-based Airflow DAG to run in a local Python environment.

## Features

- **Web Dashboard**: Monitor pipeline runs and view earthquake data
- **Real-time Data**: Fetches earthquake data from USGS API
- **PostgreSQL Storage**: Stores raw and processed earthquake data
- **Pipeline Management**: Track execution status and history
- **Responsive UI**: Bootstrap-based interface with real-time updates

## Quick Start

### Option 1: GitHub Codespaces (Recommended)

1. Click the "Code" button on GitHub and select "Create codespace on main"
2. Wait for the environment to set up (PostgreSQL and dependencies will be installed automatically)
3. Run the application:
   ```bash
   python main.py
   ```
4. Open port 5000 in your browser when prompted

### Option 2: Local Development

1. **Prerequisites**:
   - Python 3.11+
   - PostgreSQL database
   - Git

2. **Clone and Setup**:
   ```bash
   git clone <your-repo-url>
   cd earthquake-pipeline
   pip install -r codespace-requirements.txt
   ```

3. **Environment Variables**:
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost:5432/earthquake_data"
   # OR set individual variables:
   export PGHOST="localhost"
   export PGPORT="5432"
   export PGUSER="your_username"
   export PGPASSWORD="your_password"
   export PGDATABASE="earthquake_data"
   ```

4. **Run the Application**:
   ```bash
   python main.py
   ```

## Usage

1. **Dashboard**: View pipeline statistics and recent runs
2. **Run Pipeline**: Click "Run Pipeline" to fetch earthquake data for a specific date
3. **View Data**: Navigate to the "Data" page to see processed earthquake information
4. **Monitor Status**: Pipeline runs are tracked with real-time status updates

## Architecture

- **Flask Web App**: Main application with dashboard and API endpoints
- **PostgreSQL Database**: 
  - `earthquake`: Raw earthquake data
  - `stage_earthquake`: Processed earthquake data
  - `pipeline_runs`: Execution tracking
- **ETL Pipeline**: Fetches, transforms, and loads earthquake data
- **Background Processing**: Threaded pipeline execution

## Data Flow

1. User triggers pipeline via web interface
2. Pipeline fetches earthquake data from USGS API
3. Data is saved to CSV and loaded into PostgreSQL
4. Raw data is transformed and cleaned
5. Results are displayed in the web interface

## API Endpoints

- `GET /`: Main dashboard
- `POST /run_pipeline`: Trigger pipeline execution
- `GET /data`: View earthquake data with pagination
- `GET /api/earthquake_data`: JSON API for earthquake data
- `GET /api/pipeline_status/<id>`: Check pipeline execution status

## Development

The application is configured for GitHub Codespaces with:
- Pre-configured PostgreSQL database
- Automatic dependency installation
- Port forwarding for Flask app (5000) and PostgreSQL (5432)
- VS Code extensions for Python development

## Original Airflow DAG

This application was converted from a Docker-based Airflow DAG that used:
- Airflow task orchestration
- Docker containers for PostgreSQL
- Separate Python scripts for each ETL step

The conversion maintains all original functionality while adding:
- Web interface for monitoring and control
- Real-time status updates
- Better error handling and logging
- Simplified deployment without Docker dependencies

## License

This project is open source and available under the MIT License.