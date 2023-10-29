# Import the necessary dependencies.
import datetime as dt
import numpy as np
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

# Define a route to the root URL, Homepage with a list of all available routes
@app.route("/")
def welcome():
    return (
        "Welcome to Hawaii Climate Analysis API<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/temp/start<br/>"
        "/api/v1.0/temp/end<br/>"
        "<p>'start' and 'end' date should be in format MMDDYYYY.</p>"
    )

# Define a route for precipitation data.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the last data point in the database.
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query the database for precipitation data.
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= previous_year).all()

    # Close the session.
    session.close()

    # Convert the precipitation data to a dictionary and return it as JSON.
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

# Define a route for station data.
@app.route("/api/v1.0/stations")
def stations():
    # Query the database for station data.
    results = session.query(Station.station).all()

    # Close the session.
    session.close()

    # Extract the station information and return it as a JSON list.
    stations = [result[0] for result in results]
    return jsonify(stations=stations)

# Define a route for temperature data.
@app.route("/api/v1.0/tobs")
def temp_monthly():
    # Calculate the date one year ago from the last data point in the database.
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the database for temperature data for the most-active station.
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= previous_year).all()
    
    # Close the session.
    session.close()

    # Extract the temperature data and return it as a JSON list.
    temps = [result[0] for result in results]
    return jsonify(temps=temps)

# Define a route for temperature statistics with optional start and end dates.
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Convert start and end dates to datetime objects.
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y") if end else None

    # Create a list of filter conditions and use the and_ function to combine them.
    filters = [Measurement.date >= start]
    if end:
        filters.append(Measurement.date <= end)

    # Query the database for temperature statistics.
    results = session.query(*sel).filter(*filters).all()

    # Close the session.
    session.close()

    # Extract the temperature statistics and return them as a JSON list.
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


# Run the Flask app if the script is the main module.
if __name__ == "__main__":
    app.run(debug=True)
