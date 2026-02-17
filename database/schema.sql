-- This is Vendors Table
CREATE TABLE vendors (
    vendor_id INT PRIMARY KEY,
    name VARCHAR(100)
);

-- This is Ratecode Table
CREATE TABLE ratecode (
    rate_code_id INT PRIMARY KEY,
    value VARCHAR(100)
);

-- This is Location Table
CREATE TABLE location (
    location_id INT PRIMARY KEY,
    borough VARCHAR(100),
    zone VARCHAR(150),
    service_zone VARCHAR(100)
);

-- This is Trips Table
CREATE TABLE trips (
    trip_id BIGINT PRIMARY KEY,
    vendor_id INT,
    pickup_datetime DATETIME,
    dropoff_datetime DATETIME,
    passenger_count INT,
    trip_distance DECIMAL(10, 2),
    rate_code_id INT,
    store_and_fwd_flag CHAR(1),
    pu_location_id INT,
    do_location_id INT,
    payment_type INT,
    fare_amount DECIMAL(10, 2),
    extra DECIMAL(10, 2),
    mta_tax DECIMAL(10, 2),
    tip_amount DECIMAL(10, 2),
    tolls_amount DECIMAL(10, 2),
    improvement_surcharge DECIMAL(10, 2),
    total_amount DECIMAL(10, 2),
    borough TEXT,
    congestion_surcharge DECIMAL(10, 2),
    FOREIGN KEY (vendor_id) REFERENCES vendors (vendor_id),
    FOREIGN KEY (rate_code_id) REFERENCES ratecode (rate_code_id),
    FOREIGN KEY (pu_location_id) REFERENCES location (location_id),
    FOREIGN KEY (do_location_id) REFERENCES location (location_id)
);

CREATE INDEX idx_trips_pickup ON trips (pickup_datetime);

CREATE INDEX idx_trips_pu_location ON trips (pu_location_id);

CREATE INDEX idx_trips_do_location ON trips (do_location_id);

-- This is Trip Summary Table
CREATE TABLE trip_summary (
    summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    hour INTEGER,
    borough TEXT,
    trip_count INTEGER,
    total_amount REAL,
    total_distance REAL,
    total_duration_hrs REAL
);

CREATE INDEX idx_summary_lookup ON trip_summary (date, borough);