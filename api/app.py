from flask import Flask, jsonify, request
from sqlalchemy import func, extract
from datetime import datetime
from flask_cors import CORS
from config import Config
from models import db, Trip, Location, TripSummary

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

CORS(app, resources={r"/api/*": {"origins": "*"}})


def applyFilters(query, model=Trip):
    """Generic filter applicator for both raw Trips and TripSummary"""
    start = request.args.get("start_date")
    end = request.args.get("end_date")
    borough = request.args.get("borough")

    if start:
        if model == TripSummary:
            query = query.filter(TripSummary.date >= start)
        else:
            query = query.filter(Trip.pickup_datetime >= start)
    if end:
        if model == TripSummary:
            query = query.filter(TripSummary.date <= end)
        else:
            query = query.filter(Trip.pickup_datetime <= f"{end} 23:59:59")
    
    if borough and borough != 'All Boroughs':
        query = query.filter(model.borough == borough)

    return query


@app.route("/api/health")
def healthCheck():
    return jsonify({"status": "ok"})


@app.route("/api/boroughs")
def getBoroughs():
    """
     The function will retrieve all the boroughs
    """
    value = db.session.query(Location.borough).distinct().all()
    return jsonify([i[0] for i in value])


@app.route("/api/stats")
def getStats():
    """
    This function will retrieve the total number of trips, total revenue, average speed, and average distance from the TripSummary table, applying any filters specified in the request. It returns the results as a JSON object.
    """
    stats = applyFilters(db.session.query(
        func.sum(TripSummary.trip_count),
        func.sum(TripSummary.total_amount),
        func.sum(TripSummary.total_distance) / func.nullif(func.sum(TripSummary.total_duration_hrs), 0),
        func.sum(TripSummary.total_distance) / func.nullif(func.sum(TripSummary.trip_count), 0)
    ), model=TripSummary).first()

    total, revenue, avg_speed, avg_dist = stats or (0, 0, 0, 0)

    return jsonify({
        "total_trips": int(total or 0),
        "revenue": round(revenue or 0, 2),
        "avg_speed": round(avg_speed or 0, 2),
        "avg_distance": round(avg_dist or 0, 2)
    })


@app.route("/api/hourly")
def getHourlyPattern():
    """
    This function will get hourly patterns of the trips and the counts
    """
    value = applyFilters(db.session.query(
        TripSummary.hour,
        func.sum(TripSummary.trip_count)
    ), model=TripSummary).group_by(TripSummary.hour).all()

    return jsonify([{"hour": h, "count": c} for h, c in value])


@app.route("/api/patterns-borough")
def getBoroughPattern():
    """
    This function will get the patterns of the trips and the counts by borough
    """
    value = applyFilters(db.session.query(
        TripSummary.borough,
        func.sum(TripSummary.trip_count)
    ), model=TripSummary).group_by(TripSummary.borough).all()

    return jsonify([{"borough": b, "count": c} for b, c in value])


@app.route("/api/patterns-daily")
def getDailyPattern():
    """
    This function will get the daily patterns of the trips and the counts
    """
    value = applyFilters(db.session.query(
        TripSummary.date,
        func.sum(TripSummary.trip_count)
    ), model=TripSummary).group_by(TripSummary.date).all()

    return jsonify([{"date": d, "count": int(c)} for d, c in value])





if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
