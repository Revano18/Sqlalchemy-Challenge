from flask import Flask, jsonify
import pandas as pd
import numpy as np
import datetime as dt
from sqlalchemy import create_engine, inspect, text, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base



app = Flask(__name__)


# Connect to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# References each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)


# Home Route
@app.route("/")
def home():
    return(
        f"<center><h2>Welcome to the Hawaii Climate Analysis Local API</h2></center>"
        f"<center><h3>Select from one of the available routes:</h3></center>"
        f"<center>/api/v1.0/Precipitation</center>"
        f"<center>/api/v1.0/Stations</center>"
        f"<center>/api/v1.0/Tobs</center>"
        f"<center>/api/v1.0/start/end</center>"
    )

# /api/v1.0/Precipitation route
@app.route("/api/v1.0/Precipitation")
def precip():
    # Return the previous year's
    # Calculate the date one year from the last date in data set.
    PreviousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= PreviousYear).all()

    session.close()
    # Dictionary 
    Precipitation = {date: prcp for date, prcp in results}
    #Convert to json
    return jsonify(Precipitation)

# /api/v1.0/stations route
@app.route("/api/v1.0/Stations")
def stations():
    # a list of stations
    # Perform a query to retrieve the names of the stations
    results = session.query(Station.station).all()
    session.close()

    stationList = list(np.ravel(results))

    # convert to json
    return jsonify(stationList)

# /api/v1.0/tobs route
@app.route("/api/v1.0/Tobs")
def temperature(): 
    # Calculate the date one year from the last date in data set.
    PreviousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the temperatures from the most active from the past year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= PreviousYear).all()

    session.close()

    temperatureList = list(np.ravel(results))

    # return list of temp
    return jsonify(temperatureList)

# /api/v1.0/start/end and /api/v1.0/start route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None):

    # Select statement
    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:

        startDate = dt.datetime.strptime(start, "%m%d%Y")

        results = session.query(*selection).filter(Measurement.date >= startDate)

        session.close()

        temperatureList = list(np.ravel(results))

        #return the list 
        return jsonify(temperatureList)
    
    else: 

        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")


        results = session.query(*selection).\
            filter(Measurement.date >= startDate).\
            filter(Measurement.date >= endDate)

        session.close()

        temperatureList = list(np.ravel(results))

        #return the list 
        return jsonify(temperatureList)
    

# app launcher
if __name__ == '__main__':
    app.run(debug=True)