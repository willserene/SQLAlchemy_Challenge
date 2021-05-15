import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

import datetime as dt


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect database into a new model
base = automap_base()

# reflect the tables
base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = base.classes.measurement
Station = base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print("server received a request for 'Home' page")
    
    return (
        f"Available Routes:<br/>"
        f"Precipitation Data: /api/v1.0/precipitation<br/>"
        f"Station Data: /api/v1.0/stations<br/>"
        f"Temperature Data: /api/v1.0/tobs<br/>"
        f"Min, Avg, and Max Temp Data from *start date provided: /api/v1.0/temp/<start><br/>"
        f"Min, Avg, and Max Temp Data from *start date to end date provided: /api/v1.0/temp/<start>/<end><br/>"
        f"*Start Date and End Date should be provided as YYYY-MM-DD"
    )



@app.route("/api/v1.0/precipitation")
def precip():
    session = Session(engine)
    
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    precip_data = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= query_date).all()

    precipitation_list = []
    
    for date, prcp in precip_data:
        precipitation = {}
        precipitation["date"] = date
        precipitation["prcp"] = prcp
        precipitation_list.append(precipitation)
        
    session.close()

    return jsonify(precipitation_list)

# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    stationresults = session.query(Station.station).all()
   
    allstations = list(np.ravel(stationresults))
    
    session.close()

    return jsonify(allstations)

# Query the dates and temperature observations of the most active station for the last year of data.

# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    active_station = "USC00519281"
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    station_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= query_date).\
        filter(Measurement.station == active_station).all()
    most_active = list(np.ravel(station_data))

    session.close()

    return jsonify(most_active)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

@app.route("/api/v1.0/temp/<start>")
# route example: /api/v1.0/temp/YYYY-MM-DD
def tempdata_start(start = None):

    session = Session(engine)

    tempdata = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
   
    tempdata_results = list(np.ravel(tempdata))

    tmin = tempdata_results[0]
    tavg = tempdata_results[1]
    tmax = tempdata_results[2]

    tempdata_list = []
 
    tempdata_return = [{"Start Date": start},
        {"The minimum temperature on record from this day forward was": tmin},
        {"The average temperature on record from this day forward was": tavg},
        {"The maximum temperature on record from this day forward was": tmax}]
    tempdata_list.append(tempdata_return)

    session.close()

    return jsonify(tempdata_list)
    
#When given the start & the end date, calculate the 'TMIN', 'TAVG', & 'TMAX' for dates between the start & end date inclusive.

@app.route("/api/v1.0/temp/<start>/<end>")
# route example: /api/v1.0/temp/YYYY-MM-DD/YYY-MM-DD
def tempdata_daterange(start = None , end = None):

    session = Session(engine)
    
    tempdata = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    tempdata_results = list(np.ravel(tempdata))

    tmin = tempdata_results[0]
    tavg = tempdata_results[1]
    tmax = tempdata_results[2]

    tempdata_results = []
    
    tempdata_return = [{"Start Date": start}, {"End Date": end},
        {"The minimum temperature during this period of time was": tmin},
        {"The average temperature during this period of time was": tavg},
        {"The maximum temperature during this period of time was": tmax}]
        
    tempdata_results.append(tempdata_return)

    session.close()

    return jsonify(tempdata_results)

       
    
if __name__ == '__main__':
    app.run(debug=True)


