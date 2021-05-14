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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )



@app.route("/api/v1.0/precipitation")
def precip():
    session=Session(engine)
    
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


@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    
    stationresults = session.query(Station.station).all()
   
    allstations = list(np.ravel(stationresults))
    
    session.close()
    return jsonify(allstations)


@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    
    active_station = "USC00519281"
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    

    station_data = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= query_date).\
    filter(Measurement.station == active_station).all()

    
    most_active = list(np.ravel(station_data))
    session.close()
    return jsonify(most_active)


@app.route("/api/v1.0/<start>")
def start(start):

    session=Session(engine)
    
    temp_calc= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    results_temp= list(np.ravel(temp_calc))

    min_temp= results_temp[0]
    avg_temp= results_temp[1]
    max_temp= results_temp[2]

    temp_data=[]
 
    temp_dict= [{"Start Date": start},
    {"The minimum temperature for this date was": min_temp},
    {"The average temperature for this date was": avg_temp},
    {"The maximum temperature for this date was": max_temp}]
    temp_data.append(temp_dict)
    session.close()

    return jsonify(temp_data)

    
#When given the start & the end date, calculate the 'TMIN', 'TAVG', & 'TMAX' for dates between the start & end date inclusive.

@app.route("/api/v1.0/temp/<start>/<end>")
def end(start,end):
 #Date input format = 8-5-17 ISO
    session=Session(engine)
    
    #start_date=datetime.strptime(start, "%Y-%m-%d").date()

    trip_calcs= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date<=end).all()

    trip_result= list(np.ravel(trip_calcs))

    min_temp_trip= trip_result[0]
    avg_temp_trip= trip_result[1]
    max_temp_trip= trip_result[2]
    #Trip date 2016-1-1 end date 2017-1-1 # 1 Year in Hawaii!!!

    trip_data=[]
    #Create a list of dictionaries & append to empty list temp_data
    trip_dict= [{"Start Date": start},
    
    {"The minimum temperature for this date was": min_temp_trip},
    {"The average temperature for this date was": avg_temp_trip},
    {"The maximum temperature for this date was": max_temp_trip},
    {"End Date": end}]
    trip_data.append(trip_dict)
    session.close()

    return jsonify(trip_data)

#########        
    
if __name__ == '__main__':
    app.run(debug=True)



## USE FOR START AND END DATE QUERIES

# def calc_temps(start_date, end_date):
#     """TMIN, TAVG, and TMAX for a list of dates.
    
#     Args:
#         start_date (string): A date string in the format %Y-%m-%d
#         end_date (string): A date string in the format %Y-%m-%d
        
#     Returns:
#         TMIN, TAVE, and TMAX
#     """
    
#     return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
#         filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# # For example
# print(calc_temps('2012-02-28', '2012-03-05'))