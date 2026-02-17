from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    BigInteger,
    String,
    DateTime,
    DECIMAL,
    ForeignKey,
    CHAR
)
from sqlalchemy.orm import declarative_base, relationship
import os

Base = declarative_base()


# Vendors Table
class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    trips = relationship("Trip", back_populates="vendor")


# Rate Code Table
class RateCode(Base):
    __tablename__ = "ratecode"

    rate_code_id = Column(Integer, primary_key=True)
    value = Column(String(100), nullable=False)

    trips = relationship("Trip", back_populates="ratecode")


# Location Table
class Location(Base):
    __tablename__ = "location"

    location_id = Column(Integer, primary_key=True)
    borough = Column(String(100))
    zone = Column(String(150))
    service_zone = Column(String(100))

    pickup_trips = relationship(
        "Trip",
        foreign_keys="Trip.pu_location_id",
        back_populates="pickup_location"
    )

    dropoff_trips = relationship(
        "Trip",
        foreign_keys="Trip.do_location_id",
        back_populates="dropoff_location"
    )


# Trips Table
class Trip(Base):
    __tablename__ = "trips"

    trip_id = Column(BigInteger, primary_key=True, autoincrement=True)

    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"))
    pickup_datetime = Column(DateTime, nullable=False)
    dropoff_datetime = Column(DateTime, nullable=False)

    passenger_count = Column(Integer)
    trip_distance = Column(DECIMAL(10, 2))
    rate_code_id = Column(Integer, ForeignKey("ratecode.rate_code_id"))
    store_and_fwd_flag = Column(CHAR(1))

    pu_location_id = Column(Integer, ForeignKey("location.location_id"))
    do_location_id = Column(Integer, ForeignKey("location.location_id"))

    payment_type = Column(Integer)
    fare_amount = Column(DECIMAL(10, 2))
    extra = Column(DECIMAL(10, 2))
    mta_tax = Column(DECIMAL(10, 2))
    tip_amount = Column(DECIMAL(10, 2))
    tolls_amount = Column(DECIMAL(10, 2))
    improvement_surcharge = Column(DECIMAL(10, 2))
    total_amount = Column(DECIMAL(10, 2))
    congestion_surcharge = Column(DECIMAL(10, 2))

    # Relationships
    vendor = relationship("Vendor", back_populates="trips")
    ratecode = relationship("RateCode", back_populates="trips")

    pickup_location = relationship(
        "Location",
        foreign_keys=[pu_location_id],
        back_populates="pickup_trips"
    )

    dropoff_location = relationship(
        "Location",
        foreign_keys=[do_location_id],
        back_populates="dropoff_trips"
    )


# Create Database Tables
if __name__ == "__main__":
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    db_name = os.getenv("DB_NAME")

    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}")

    Base.metadata.create_all(engine)
