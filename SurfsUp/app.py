#import dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Setup Database
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect = True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Route to homepage
# List all available routes
@app.route('/')
def welcome():
    """List of available routes"""
    return (
        "Welcome to the home page! Here is a list of available routes<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year of most active station: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date: /api/v1.0/&lt;start&gt;<br/>"
        f"Temperature stat from start to end dates: /api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# Precipitation route
# List of dictionaries for date and precipitation of last 12 months of data
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    one_year = dt.date(last_date.year -1, last_date.month, last_date.day)
    prcp_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year).all()
    session.close()

    precipitation = []

    for date, prcp in prcp_query:
        prcp_dict = {}
        prcp_dict['Date'] = date
        prcp_dict['Precipitation'] = prcp
        precipitation.append(prcp_dict)
    return jsonify(precipitation)

# Station route
# List of stations with id, station, and name
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    stations_query = session.query(Station.station, Station.id, Station.name).all()
    session.close()

    station_list = []

    for station, id, name in stations_query:
        station_dict = {}
        station_dict['ID'] = id
        station_dict['Station'] = station
        station_dict['Name'] = name
        station_list.append(station_dict)
    return jsonify(station_list)

###add only for most active station******
# Tobs route
# Dates and temperature observations for the previous year of most active station
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    one_year = dt.date(last_date.year -1, last_date.month, last_date.day)
    most_active = most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()
    most_active_station = most_active[0] 
    sel = [Measurement.date, Measurement.tobs]
    tobs_query = session.query(*sel).filter(Measurement.date >= one_year).filter(Measurement.station == most_active_station).all()
    session.close()

    tobs_list = []

    for date, tob in tobs_query:
        tobs_dict = {}
        tobs_dict['Date'] = date
        tobs_dict['tobs'] = tob
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

# JSON list of min, max and avg temperatures from a specific start date
@app.route('/api/v1.0/<start>')
def start_date(start):
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs), Measurement.station]
    start_date_tobs_data = session.query(*sel).filter(Measurement.date >= start).all()
    session.close()

    start_date_tobs_list = []

    for min, max, avg, station in start_date_tobs_data:
        start_date_tobs_dict = {}
        start_date_tobs_dict['Min'] = min
        start_date_tobs_dict['Max'] = max
        start_date_tobs_dict['Avg'] = avg
        start_date_tobs_dict['Station'] = station
        start_date_tobs_list.append(start_date_tobs_dict)
    return jsonify(start_date_tobs_list)

# JSON list for min, max and average temperatures between given start and end dates
@app.route('/api/v1.0/<start>/<end>')
def start_end_date(start,end):
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs), Measurement.station]
    start_end_date_tobs_data = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    start_end_date_tobs_list = []

    for min, max, avg, station in start_end_date_tobs_data:
        start_end_date_tobs_dict = {}
        start_end_date_tobs_dict['Min'] = min
        start_end_date_tobs_dict['Max'] = max
        start_end_date_tobs_dict['Avg'] = avg
        start_end_date_tobs_dict['Station'] = station
        start_end_date_tobs_list.append(start_end_date_tobs_dict)
    return jsonify(start_end_date_tobs_list)


if __name__ == '__main__':
    app.run(debug=True)