# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    """Return last 12 months of precipitation data"""

    precip_dict = {}
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').order_by(Measurement.date).all()

    for result in results:
        precip_dict[result[0]] = result[1]

    session.close()

    return jsonify(precip_dict)


@app.route("/api/v1.0/stations")
def stations():

    """Return a JSON list of stations from the dataset"""

    # list_station_names = []

    station_names = session.query(Station.station).all()
  
    station = list(np.ravel(station_names))

    session.close()
    
    return jsonify(station)


@app.route("/api/v1.0/tobs")
def tobs():

    """Return a list of temperature observations of the most-active station for th eprevious year of data"""

    # list_tobs = []

    most_active_tobs = session.query(Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= '2016-08-18').all()

    tobs = list(np.ravel(most_active_tobs))

    # for tob in most_active_tobs: 
    #     list_tobs.append(tob)
    
    session.close()

    return jsonify(tobs)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start, end=None):

    if not end:
        start_dt = datetime.datetime.strptime(start, '%m%d%Y')
        min_avg_max = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).all()
        re = list(np.ravel(min_avg_max))
        return jsonify(re)
    
    start_dt = datetime.datetime.strptime(start, '%m%d%Y')
    end_dt = datetime.datetime.strptime(end, '%m%d%Y')
    min_max_avg_start_end = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt).all()
   
    session.close()

    res = list(np.ravel(min_max_avg_start_end))
    return jsonify(res)


if __name__ == '__main__':
    app.run(debug=True)

