import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect existing database into new model

Base = automap_base()
# reflect tables
Base.prepare(engine)
# save reference to tables
Measurement = Base.classes.measurement
Station = Base.classes.station
# create session from python to DB
session = Session(engine)

# Flask setup
app = Flask(__name__)

# route setup
@app.route("/")
def welcome():
    return(
    f"Welcome to the Hawaii Climate Analysis API<br/>"
    f"Available Routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/temp/start<br/>"
    f"/api/v1.0/temp/start/end<br/>"
    f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
    )


@app.route("/api/v1.0/precipitation")
def preciptation():
    # Retrieve last 12 months of data
    previous_year_date = dt.date(2017,8,23) - dt.timedelta(days = 365)
    preciptation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_year_date).all()

    session.close()
    # create dictonary
    precip = { date: prcp for date, prcp in preciptation }

    # json representation of dictionary
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    # list of stations from dataset
    results = session.query(Station.station).all()
    session.close()

    # create dictonary
    stations = list(np.ravel(results))

     # json representation of dictionary
    return jsonify(stations = stations)

@app.route("/api.v1.0/tobs")
def temp_monthly():
    # Observaton of most active station of previous year
    previous_year_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= previous_year_date).all()
    
    session.close()

    # create dictonary
    temps = list(np.ravel(results))

    # json representation of dictionary
    return jsonify(temps = temps)
        

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
def stats(start = None, end = None):
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start,"%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()
        # create dictonary
        temps = list(np.ravel(results))
        # json representation of dictionary
        return jsonify(temps=temps)

    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()
    # create dictonary
    temps = list(np.ravel(results))
    # json representation of dictionary
    return jsonify(temps=temps)


if __name__ == "__main__":
    app.run(debug=True)





