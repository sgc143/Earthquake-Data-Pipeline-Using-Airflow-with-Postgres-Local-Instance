from datetime import datetime
from database import db

class PipelineRun(db.Model):
    """Model to track pipeline execution runs."""
    __tablename__ = 'pipeline_runs'
    
    id = db.Column(db.Integer, primary_key=True)
    execution_date = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, running, completed, failed
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<PipelineRun {self.id}: {self.execution_date} - {self.status}>'

class EarthquakeData(db.Model):
    """Model for raw earthquake data."""
    __tablename__ = 'earthquake'
    
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.BigInteger, nullable=False)
    place = db.Column(db.String(255), nullable=True)
    magnitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    depth = db.Column(db.Float, nullable=True)
    file_name = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<EarthquakeData {self.id}: {self.magnitude} at {self.place}>'

class StageEarthquake(db.Model):
    """Model for transformed earthquake data."""
    __tablename__ = 'stage_earthquake'
    
    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime, nullable=False)
    dt = db.Column(db.Date, nullable=False)
    place = db.Column(db.String(255), nullable=True)
    magnitude = db.Column(db.Float, nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<StageEarthquake {self.id}: {self.magnitude} at {self.place}>'
