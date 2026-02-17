from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Vendor(db.Model):
    __tablename__ = "vendors"
    vendor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


class RateCode(db.Model):
    __tablename__ = "ratecode"
    rate_code_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100))


class Location(db.Model):
    __tablename__ = "location"
    location_id = db.Column(db.Integer, primary_key=True)
    borough = db.Column(db.String(100))
    zone = db.Column(db.String(150))
    service_zone = db.Column(db.String(100))


class Trip(db.Model):
    __tablename__ = "trips"
    trip_id = db.Column(db.BigInteger, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.vendor_id"))
    pickup_datetime = db.Column(db.DateTime)
    dropoff_datetime = db.Column(db.DateTime)
    passenger_count = db.Column(db.Integer)
    trip_distance = db.Column(db.Float)
    rate_code_id = db.Column(db.Integer, db.ForeignKey("ratecode.rate_code_id"))
    store_and_fwd_flag = db.Column(db.String(1))
    pu_location_id = db.Column(db.Integer, db.ForeignKey("location.location_id"))
    do_location_id = db.Column(db.Integer, db.ForeignKey("location.location_id"))
    payment_type = db.Column(db.Integer)
    fare_amount = db.Column(db.Float)
    extra = db.Column(db.Float)
    mta_tax = db.Column(db.Float)
    tip_amount = db.Column(db.Float)
    tolls_amount = db.Column(db.Float)
    improvement_surcharge = db.Column(db.Float)
    total_amount = db.Column(db.Float)
    borough = db.Column(db.String(50))
    congestion_surcharge = db.Column(db.Float)

class TripSummary(db.Model):
    __tablename__ = 'trip_summary'
    summary_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), index=True)
    hour = db.Column(db.Integer)
    borough = db.Column(db.String(50), index=True)
    trip_count = db.Column(db.Integer)
    total_amount = db.Column(db.Float)
    total_distance = db.Column(db.Float)
    total_duration_hrs = db.Column(db.Float)
