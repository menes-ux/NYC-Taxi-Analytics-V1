import pandas as pd
from sqlalchemy import create_engine
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.dirname(BASE_DIR)

db_path = os.path.join(ROOT_DIR, "database", "nycTaxi.db")
engine = create_engine(f"sqlite:///{db_path}")


def loadLocations():
    """
    This function will load the locations from the taxi_zone_lookup.csv file
    """
    file_path = os.path.join(ROOT_DIR, "taxi_zone_lookup.csv")
    df = pd.read_csv(file_path)
    df.columns = ["location_id", "borough", "zone", "service_zone"]
    df.to_sql("location", engine, if_exists="replace", index=False)
    print("Locations Loaded")


def loadTrips():
    """
    This function will load the trips from the yellow_tripdata_2019-01.csv file
    """
    file_path = os.path.join(ROOT_DIR, "yellow_tripdata_2019-01.csv")
    loc_path = os.path.join(ROOT_DIR, "taxi_zone_lookup.csv")
    loc_df = pd.read_csv(loc_path)
    loc_df.columns = ["location_id", "borough", "zone", "service_zone"]
    loc_map = loc_df.set_index("location_id")["borough"].to_dict()

    chunksize = 100000
    first_chunk = True
    total_rows = 0
    total_loaded = 0
    log_path = os.path.join(BASE_DIR, "taxiCleanUpLog.csv")
    exclusion_counts = {}

    pd.DataFrame(columns=["trip_id", "reason", "value"]).to_csv(log_path, index=False)

    print(f"Loading Trips from {file_path}...")

    for df in pd.read_csv(file_path, chunksize=chunksize):
        df["trip_id"] = range(total_rows, total_rows + len(df))
        total_rows += len(df)

        df.rename(columns={
            "VendorID": "vendor_id",
            "tpep_pickup_datetime": "pickup_datetime",
            "tpep_dropoff_datetime": "dropoff_datetime",
            "PULocationID": "pu_location_id",
            "DOLocationID": "do_location_id",
            "RatecodeID": "rate_code_id"
        }, inplace=True)

        log_entries = []
        before = len(df)

        df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
        df["dropoff_datetime"] = pd.to_datetime(df["dropoff_datetime"], errors="coerce")

        def flagDrop(dataframe, condition, reason, col):
            flagged = dataframe[condition]
            for i in flagged.index:
                log_entries.append({"trip_id": int(dataframe.at[i, "trip_id"]),
                                    "reason": reason, "value": str(dataframe.at[i, col])})
            exclusion_counts[reason] = exclusion_counts.get(reason, 0) + len(flagged)
            return dataframe[~condition]

        df = flagDrop(df, df["pickup_datetime"].dt.year != 2019,
                           "out_of_range_year", "pickup_datetime")

        df = flagDrop(df, df["trip_distance"] <= 0, "zero_negative_distance", "trip_distance")
        df = flagDrop(df, df["trip_distance"] > 200, "extreme_distance", "trip_distance")

        df = flagDrop(df, df["fare_amount"] <= 0, "zero_negative_fare", "fare_amount")

        duplicatedColumns = ["pickup_datetime", "dropoff_datetime", "pu_location_id", "do_location_id", "trip_distance", "total_amount"]
        df = flagDrop(df, df.duplicated(subset=duplicatedColumns, keep="first"), "duplicate_row", "total_amount")

        if log_entries:
            pd.DataFrame(log_entries).to_csv(log_path, mode="a", header=False, index=False)

        removed = before - len(df)
        if removed > 0:
            print(f"    Cleaned: removed {removed} bad rows")

        df["borough"] = df["pu_location_id"].map(loc_map)

        if_exists = "replace" if first_chunk else "append"
        df.to_sql("trips", engine, if_exists=if_exists, index=False)
        first_chunk = False
        total_loaded += len(df)
        print(f"Loaded {total_loaded} clean rows ({total_rows} processed)...")

    total_excluded = sum(exclusion_counts.values())
    
    print(f"Total processed: {total_rows}  |  Loaded: {total_loaded}  |  Excluded: {total_excluded}")
    for reason, count in sorted(exclusion_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {reason}: {count}")
    print(f"Cleanup log saved to: {log_path}")
    print("Trips Loaded Successfully")


def createIndexes():
    """
    This function will create indexes for the database
    """ 
    print("Adding database indexes for performance...")
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_trips_pickup ON trips(pickup_datetime);",
        "CREATE INDEX IF NOT EXISTS idx_trips_pu_location ON trips(pu_location_id);",
        "CREATE INDEX IF NOT EXISTS idx_trips_do_location ON trips(do_location_id);",
        "CREATE INDEX IF NOT EXISTS idx_trips_borough_pickup ON trips(borough, pickup_datetime);"
    ]

    for sql in indexes:
        print(f"Executing: {sql}")
        cursor.execute(sql)

    conn.commit()
    conn.close()
    print("Indexes created. Database is now optimized.")


def createSummaryTable():
    """
    This function will pre-aggregate data into trip_summary table 
    for sub-second dashboard performance.
    """
    print("Pre-aggregating data for extreme performance (0.1s target)...")
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trip_summary (
            summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            hour INTEGER,
            borough TEXT,
            trip_count INTEGER,
            total_amount REAL,
            total_distance REAL,
            total_duration_hrs REAL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_summary_lookup ON trip_summary(date, borough)")

    cursor.execute("DELETE FROM trip_summary")
    cursor.execute("""
        INSERT INTO trip_summary (
            date, hour, borough, trip_count, total_amount, 
            total_distance, total_duration_hrs
        )
        SELECT 
            date(pickup_datetime) as date,
            CAST(strftime('%H', pickup_datetime) AS INTEGER) as hour,
            borough,
            COUNT(*) as trip_count,
            SUM(total_amount) as total_amount,
            SUM(trip_distance) as total_distance,
            SUM((julianday(dropoff_datetime) - julianday(pickup_datetime)) * 24) as total_duration_hrs
        FROM trips
        WHERE borough IS NOT NULL
        GROUP BY date, hour, borough
    """)

    conn.commit()
    conn.close()
    print("Completed summarization process")


if __name__ == "__main__":
    loadLocations()
    loadTrips()
    createIndexes()
    createSummaryTable()
