import os
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from earthquake_pipeline import EarthquakePipeline
from database import db
from models import PipelineRun, EarthquakeData, StageEarthquake
from config import Config


class Base(DeclarativeBase):
    pass


# create the app
app = Flask(__name__)
app.config.from_object(Config)

# initialize the app with the extension
db.init_app(app)

# Initialize pipeline
pipeline = EarthquakePipeline()

@app.route('/')
def index():
    """Main dashboard showing recent pipeline runs and earthquake data."""
    recent_runs = PipelineRun.query.order_by(PipelineRun.created_at.desc()).limit(10).all()
    total_earthquakes = EarthquakeData.query.count()
    latest_data = StageEarthquake.query.order_by(StageEarthquake.ts.desc()).limit(5).all()
    
    return render_template('index.html', 
                         recent_runs=recent_runs,
                         total_earthquakes=total_earthquakes,
                         latest_data=latest_data)

@app.route('/run_pipeline', methods=['POST'])
def run_pipeline():
    """Trigger the earthquake data pipeline."""
    execution_date = request.form.get('execution_date')
    if not execution_date:
        execution_date = datetime.now().strftime('%Y-%m-%d')
    
    # Create pipeline run record
    pipeline_run = PipelineRun(
        execution_date=execution_date,
        status='running',
        started_at=datetime.now()
    )
    db.session.add(pipeline_run)
    db.session.commit()
    
    # Run pipeline in background thread
    def run_pipeline_async():
        with app.app_context():
            try:
                # Step 1: Fetch data
                csv_path = pipeline.fetch_data_to_local_csv(execution_date)
                
                # Step 2: Load to PostgreSQL
                if csv_path:
                    pipeline.load_csv_to_postgres(csv_path)
                
                # Step 3: Transform data
                pipeline.transform_in_postgres(execution_date, execution_date)
                
                # Update pipeline run as completed
                pipeline_run.status = 'completed'
                pipeline_run.completed_at = datetime.now()
                pipeline_run.message = f'Successfully processed data for {execution_date}'
                
            except Exception as e:
                pipeline_run.status = 'failed'
                pipeline_run.completed_at = datetime.now()
                pipeline_run.message = f'Error: {str(e)}'
            
            db.session.commit()
    
    # Start background thread
    thread = threading.Thread(target=run_pipeline_async)
    thread.daemon = True
    thread.start()
    
    flash(f'Pipeline started for {execution_date}', 'success')
    return redirect(url_for('index'))

@app.route('/api/pipeline_status/<int:run_id>')
def pipeline_status(run_id):
    """API endpoint to check pipeline status."""
    run = PipelineRun.query.get_or_404(run_id)
    return jsonify({
        'id': run.id,
        'status': run.status,
        'execution_date': run.execution_date,
        'started_at': run.started_at.isoformat() if run.started_at else None,
        'completed_at': run.completed_at.isoformat() if run.completed_at else None,
        'message': run.message
    })

@app.route('/api/earthquake_data')
def earthquake_data_api():
    """API endpoint to get earthquake data."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    earthquakes = StageEarthquake.query.order_by(StageEarthquake.ts.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'earthquakes': [{
            'timestamp': eq.ts.isoformat(),
            'date': eq.dt.isoformat(),
            'place': eq.place,
            'magnitude': eq.magnitude,
            'latitude': eq.latitude,
            'longitude': eq.longitude
        } for eq in earthquakes.items],
        'total': earthquakes.total,
        'pages': earthquakes.pages,
        'current_page': earthquakes.page
    })

@app.route('/data')
def data_view():
    """View earthquake data with pagination."""
    page = request.args.get('page', 1, type=int)
    earthquakes = StageEarthquake.query.order_by(StageEarthquake.ts.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('data.html', earthquakes=earthquakes)

with app.app_context():
    # Import models to ensure tables are created
    from models import PipelineRun, EarthquakeData, StageEarthquake
    
    # Create all tables
    db.create_all()
    
    # Initialize pipeline database
    pipeline.create_database()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
