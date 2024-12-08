# Import the dependencies
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

#################################################
# Database Setup
#################################################

# Create an engine to connect to the SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Set up Flask app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Homepage route: Lists available routes
@app.route("/")
def home():
    """Landing page that lists available routes"""
    return (
        f"Welcome to the Climate App API!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&ltstart&gt<br>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt"
    )

# Precipitation route: Returns precipitation data as a dictionary of date and precipitation for the last 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns precipitation data for the last 12 months as a dictionary"""
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query the precipitation data for the last year
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()
    
    # Convert query results to a dictionary (date: precipitation)
    precip_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precip_dict)

# Stations route: Returns a list of stations
@app.route("/api/v1.0/stations")
def stations():
    """Returns a list of all stations in the dataset"""
    stations_data = session.query(Station.station).all()
    stations_list = [station[0] for station in stations_data]
    return jsonify(stations_list)

# Temperature Observations (TOBS) route: Returns the temperature observations for the most active station
@app.route("/api/v1.0/tobs")
def tobs():
    """Returns temperature observations (TOBS) for the most active station (USC00519281)"""
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query temperature observations for the most active station (USC00519281)
    tobs_data = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_ago).all()
    
    # Extract temperatures from the query result
    tobs_list = [t[0] for t in tobs_data]
    return jsonify(tobs_list)

# Start date route: Returns the min, max, and average temperatures from the start date to the most recent date
@app.route("/api/v1.0/<start>")
def start(start):
    """Returns the min, max, and average temperatures from the start date to the most recent date"""
    temperature_stats = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.max(Measurement.tobs).label('max_temp'),
        func.avg(Measurement.tobs).label('avg_temp')
    ).filter(Measurement.date >= start).all()
    
    stats = temperature_stats[0]
    return jsonify({
        "Start Date": start,
        "Min Temperature": stats.min_temp,
        "Max Temperature": stats.max_temp,
        "Avg Temperature": stats.avg_temp
    })

# Start and End date route: Returns the min, max, and average temperatures for a given start and end date
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Returns the min, max, and average temperatures from the start date to the end date"""
    temperature_stats = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.max(Measurement.tobs).label('max_temp'),
        func.avg(Measurement.tobs).label('avg_temp')
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    stats = temperature_stats[0]
    return jsonify({
        "Start Date": start,
        "End Date": end,
        "Min Temperature": stats.min_temp,
        "Max Temperature": stats.max_temp,
        "Avg Temperature": stats.avg_temp
    })

# Close the session when the app is stopped
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

if __name__ == "__main__":
    app.run(debug=True)
