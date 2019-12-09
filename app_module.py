import datetime as dt 
import numpy as np 
import pandas as pd 
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base 
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
engine=create_engine("sqlite:///hawaii.sqlite")
Base=automap_base()
Base.prepare(engine,reflect=True)
Measurement=Base.classes.measurement
Station=Base.classes.station
session=Session(engine)
#set up flask
app=Flask(__name__)
@app.route("/")
def welcome():
    return(
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end<br/>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    precipitation=session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date>=prev_year).all()
    precip={date:prcp for date,prcp in precipitation}
    return jsonify(precip)
@app.route("/api/v1.0/stations")
def stations():
    results=session.query(Station.station).all()
    stations=list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    max_date_str = session.query(func.max(Measurement.date)).all()[0][0]
    max_date = dt.datetime.strptime(max_date_str, '%Y-%m-%d').date() 
    if ((dt.date.today().month == max_date.month) & (dt.date.today().day > max_date.day)) | (dt.date.today().month > max_date.month):
        one_year_ago = (max_date - dt.timedelta(days=365)).year
        prev_year = dt.date(one_year_ago, dt.date.today().month, dt.date.today().day)
    else:
        prev_year = dt.date(max_date.year, dt.date.today().month, dt.date.today().day)


    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)
