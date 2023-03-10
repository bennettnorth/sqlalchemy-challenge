
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
base.prepare(autoload_with=engine)
# reflect the tables
base.classes.keys()


# Save references to each table

measurement = base.classes.measurement
station = base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def all():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(bind=engine)

    """Return the last 12 months of precipitation data"""
    # Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value
     #Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    one_year = dt.date.fromisoformat(most_recent[0]) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year).all()
    precip_dict = {precipitation[i][0]: precipitation[i][1] for i in range(len(precipitation))}
    
    session.close()

  
    return jsonify(precip_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(bind=engine)

    """Return a JSON list of stations"""
    # Query all stations
    station_names = session.query(station.station, station.name).all()
    # convert rows to dictionary
    station_dict = {station_names[i][0]: station_names[i][1] for i in range(len(station_names))}
    # close session
    session.close()
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the dates and temperature observations of the most-active station for the previous year"""
    yearly_tobs = session.query(measurement.date, measurement.tobs).filter(measurement.date >= dt.date(2017, 8, 23)).filter(measurement.station == 'USC00519281').all()
    
    tobs_dict = {yearly_tobs[i][0]: yearly_tobs[i][1] for i in range(len(yearly_tobs))}

    session.close()

    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(bind=engine)

    """Return a list of temperatures"""
    temperature_data = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).all()

    temperature_dict= {temperature_data[i][0]: temperature_data[i][1] for i in range(len(temperature_data))}
    session.close()


    return jsonify(temperature_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(bind=engine)

    """Return a list of temperatures"""
    temperature_data = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()

    temperature_dict = {temperature_data[i][0]: temperature_data[i][1] for i in range(len(temperature_data))}

    session.close()

    return jsonify(temperature_dict)

if __name__ == '__main__':
    app.run(debug=True)
