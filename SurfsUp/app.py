from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

# Set up the Flask app
app = Flask(__name__)

# Set up the SQLAlchemy engine and session
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False})
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Home Route - Shows all available routes
@app.route("/")
def home():
    return (
        f"Welcome to the Climate API!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&lt;start&gt;<br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>"
    )

# Route to return precipitation data for the last 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Find the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    # Calculate the date one year ago from the most recent date
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query the last 12 months of precipitation data
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Convert to a dictionary
    precip_dict = {date: prcp for date, prcp in precip_data}

    return jsonify(precip_dict)

# Route to return a list of all stations
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    stations = session.query(Station.station, Station.name).all()

    # Convert the result to a list of dictionaries
    stations_list = [{"station": station, "name": name} for station, name in stations]

    return jsonify(stations_list)

# Route to return temperature observations for the most active station
@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    # Calculate the date one year ago
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Get the most active station
    active_station = session.query(Measurement.station, func.count(Measurement.id).label('observation_count')).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).first()

    most_active_station_id = active_station.station

    # Query the temperature observations for the most active station for the last 12 months
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the result to a list of dictionaries
    tobs_list = [{"date": date, "temperature": tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)

# Route to return temperature statistics for a given start date
@app.route("/api/v1.0/<start>")
def start_stats(start):
    # Query the temperature statistics for the start date
    stats = session.query(
        func.min(Measurement.tobs).label('TMIN'),
        func.avg(Measurement.tobs).label('TAVG'),
        func.max(Measurement.tobs).label('TMAX')
    ).filter(Measurement.date >= start).all()

    # Convert to a dictionary
    stats_dict = {"TMIN": stats[0].TMIN, "TAVG": stats[0].TAVG, "TMAX": stats[0].TMAX}

    return jsonify(stats_dict)

# Route to return temperature statistics for a start and end date
@app.route("/api/v1.0/<start>/<end>")
def start_end_stats(start, end):
    # Query the temperature statistics for the start and end date
    stats = session.query(
        func.min(Measurement.tobs).label('TMIN'),
        func.avg(Measurement.tobs).label('TAVG'),
        func.max(Measurement.tobs).label('TMAX')
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert to a dictionary
    stats_dict = {"TMIN": stats[0].TMIN, "TAVG": stats[0].TAVG, "TMAX": stats[0].TMAX}

    return jsonify(stats_dict)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
